// ============================================================================
// Echiquier interactif -- ngx-chess-board + horloge + historique navigable
// ============================================================================

import {
  Component, computed, OnDestroy, signal, ViewChild,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DecimalPipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { NgxChessBoardModule, NgxChessBoardView } from 'ngx-chess-board';

import { ServiceEtatPartie } from '../../coeur/partie/application/service-etat-partie';
import { ServiceAgent } from '../../coeur/agent/application/service-agent';
import { ReponseAgentLlm } from '../../coeur/agent/domaine/modeles';
import { ComposantPanneauRecommandations } from
  '../panneau-recommandations/composant-panneau-recommandations';

const FEN_POSITION_INITIALE =
  'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

// ------------------------------------------------------------------
// HttpErrorResponse (Angular) n'herite PAS de Error natif -- sans ce
// traitement dedie, String(e) retombe sur Object.prototype.toString()
// et affiche litteralement "[object Object]" (bug reel rencontre en
// production sur agent-llm/invoke lors d'un 422/401 backend).
// ------------------------------------------------------------------
function extraireMessageErreur(e: unknown): string {
  if (e instanceof HttpErrorResponse) {
    const detail = e.error?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d) => d.msg ?? JSON.stringify(d)).join(', ');
    }
    return `Erreur ${e.status} : ${e.statusText}`;
  }
  if (e instanceof Error) {
    return e.message;
  }
  return String(e);
}

interface EntreeHistorique {
  numero   : number;    // 1, 2, 3... (demi-coup)
  trait    : 'blancs' | 'noirs';
  fen      : string;    // Position APRES ce coup -- permet setFEN() direct,
                         // sans dependre d'un rejeu coup par coup.
  notation : string;    // Ex. "e4" -- au mieux (cf. extraireNotation())
}

@Component({
  selector: 'app-echiquier',
  standalone: true,
  imports: [NgxChessBoardModule, FormsModule, DecimalPipe, ComposantPanneauRecommandations],
  templateUrl: './composant-echiquier.html',
  styleUrl: './composant-echiquier.css',
})
export class ComposantEchiquier implements OnDestroy {
  @ViewChild('tableau', { static: false }) tableau!: NgxChessBoardView;

  // -- Recommandations de l'agent --
  reponse = signal<ReponseAgentLlm | null>(null);
  enCoursAnalyse = signal(false);
  erreurAnalyse = signal<string | null>(null);

  // ------------------------------------------------------------------
  // Barre d'evaluation : pourcentage de hauteur "blancs" (0-100).
  // 50 = equilibre. Formule sigmoide (meme principe que Lichess/
  // chess.com) : une grosse avance approche 95-98% sans jamais
  // atteindre un plafond dur, plus lisible qu'une echelle lineaire ou
  // +1000cp et +300cp semblent presque pareils.
  // ------------------------------------------------------------------
  pourcentageBlancs = computed<number>(() => {
    const evaluation = this.reponse()?.evaluation;
    if (!evaluation) {
      return 50;
    }
    if (evaluation.type === 'mate') {
      // Mate en N : le signe indique qui mate (+ blancs, - noirs).
      return evaluation.valeur > 0 ? 98 : 2;
    }
    const cp = evaluation.valeur;
    const pourcentage = 50 + 50 * (2 / (1 + Math.exp(-0.004 * cp)) - 1);
    return Math.max(2, Math.min(98, pourcentage));
  });

  // -- Historique, navigable en arriere/avant --
  historique = signal<EntreeHistorique[]>([]);
  indexAffiche = signal(0);    // 0 = position initiale, historique.length = position en direct
  enTrainDeConsulter = computed(
    () => this.indexAffiche() < this.historique().length,
  );

  // -- Horloge --
  minutesSelectionnees = signal(10);
  tempsBlancs = signal(10 * 60);    // secondes
  tempsNoirs = signal(10 * 60);
  traitBlancs = signal(true);
  horlogeActive = signal(false);
  private intervalleHorloge?: ReturnType<typeof setInterval>;

  constructor(
    private readonly etatPartie: ServiceEtatPartie,
    private readonly serviceAgent: ServiceAgent,
  ) {}

  ngOnDestroy(): void {
    this.arreterHorloge();
  }

  // ------------------------------------------------------------------
  // Jouer un coup (reel, sur le plateau -- pas une navigation d'historique)
  // ------------------------------------------------------------------
  async surCoupJoue(): Promise<void> {
    await this.traiterCoupJoue();
  }

  // ------------------------------------------------------------------
  // Jouer un coup SUGGERE (clic sur un coup theorique, ou sur un coup
  // detecte en gras dans l'explication du LLM) -- execute reellement
  // le coup sur le plateau via move(), puis meme traitement qu'un coup
  // joue a la souris. Protege contre un coup illegal ou hallucine par
  // le LLM (jamais valide contre la position reelle avant d'arriver
  // ici) : ngx-chess-board ne documente pas son comportement en cas de
  // coup invalide, donc capture large plutot que de risquer un etat
  // de plateau corrompu.
  // ------------------------------------------------------------------
  async jouerCoupSuggere(uci: string): Promise<void> {
    try {
      this.tableau.move(uci);
    } catch {
      this.erreurAnalyse.set(`Coup impossible a jouer dans cette position : ${uci}`);
      return;
    }
    await this.traiterCoupJoue();
  }

  private async traiterCoupJoue(): Promise<void> {
    const fen = this.tableau.getFEN();

    // Si on jouait depuis une position passee (historique consulte),
    // les coups futurs sont abandonnes -- meme comportement que
    // Lichess/chess.com en mode analyse.
    const historiqueActuel = this.historique();
    const indexTronque = this.indexAffiche();
    const nouvelleEntree: EntreeHistorique = {
      numero: indexTronque + 1,
      trait: this.traitBlancs() ? 'blancs' : 'noirs',
      fen,
      notation: this.extraireNotation(indexTronque),
    };
    this.historique.set([...historiqueActuel.slice(0, indexTronque), nouvelleEntree]);
    this.indexAffiche.set(indexTronque + 1);

    this.traitBlancs.set(!this.traitBlancs());
    this.etatPartie.definirFen(fen);

    if (!this.horlogeActive()) {
      this.demarrerHorloge();
    }

    this.enCoursAnalyse.set(true);
    this.erreurAnalyse.set(null);
    try {
      const reponse = await this.serviceAgent.analyserPositionAvecLlm(
        fen, this.etatPartie.idSession(),
      );
      this.reponse.set(reponse);
    } catch (e) {
      this.erreurAnalyse.set(extraireMessageErreur(e));
    } finally {
      this.enCoursAnalyse.set(false);
    }
  }

  // ------------------------------------------------------------------
  // Extrait la notation du dernier coup depuis getMoveHistory() --
  // le format exact renvoye par ngx-chess-board n'est PAS documente,
  // donc lecture defensive : on essaie les formes plausibles, et on
  // se replie sur un libelle generique si rien ne correspond, plutot
  // que de planter. La navigation (back/forward) ne depend jamais de
  // cette fonction -- elle reste basee sur le FEN, robuste par nature.
  // ------------------------------------------------------------------
  private extraireNotation(indexAvantCoup: number): string {
    try {
      const historiqueBrut: unknown = this.tableau.getMoveHistory();
      if (!Array.isArray(historiqueBrut) || historiqueBrut.length === 0) {
        return `Coup ${indexAvantCoup + 1}`;
      }
      const dernier = historiqueBrut[historiqueBrut.length - 1];

      if (typeof dernier === 'string') {
        return dernier;
      }
      if (dernier && typeof dernier === 'object') {
        const candidat = (dernier as Record<string, unknown>)['san']
          ?? (dernier as Record<string, unknown>)['move']
          ?? (dernier as Record<string, unknown>)['notation'];
        if (typeof candidat === 'string') {
          return candidat;
        }
      }
    } catch {
      // getMoveHistory() indisponible ou format inattendu -- repli silencieux.
    }
    return `Coup ${indexAvantCoup + 1}`;
  }

  // ------------------------------------------------------------------
  // Navigation dans l'historique -- setFEN() direct, pas de rejeu
  // ------------------------------------------------------------------
  allerA(index: number): void {
    const entrees = this.historique();
    const fen = index === 0 ? FEN_POSITION_INITIALE : entrees[index - 1].fen;
    this.tableau.setFEN(fen);
    this.indexAffiche.set(index);
  }

  reculer(): void {
    if (this.indexAffiche() > 0) {
      this.allerA(this.indexAffiche() - 1);
    }
  }

  avancer(): void {
    if (this.indexAffiche() < this.historique().length) {
      this.allerA(this.indexAffiche() + 1);
    }
  }

  // ------------------------------------------------------------------
  // Horloge -- ne decompte que sur la position EN DIRECT
  // ------------------------------------------------------------------
  private demarrerHorloge(): void {
    this.horlogeActive.set(true);
    this.intervalleHorloge = setInterval(() => {
      if (this.enTrainDeConsulter()) {
        return;    // Historique consulte : horloge en pause
      }
      const enTrain = this.traitBlancs() ? this.tempsBlancs : this.tempsNoirs;
      const nouvelleValeur = Math.max(0, enTrain() - 1);
      enTrain.set(nouvelleValeur);
      if (nouvelleValeur === 0) {
        this.arreterHorloge();
      }
    }, 1000);
  }

  private arreterHorloge(): void {
    if (this.intervalleHorloge) {
      clearInterval(this.intervalleHorloge);
      this.intervalleHorloge = undefined;
    }
    this.horlogeActive.set(false);
  }

  formaterTemps(secondes: number): string {
    const m = Math.floor(secondes / 60);
    const s = secondes % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  // ------------------------------------------------------------------
  // Nouvelle partie -- reinitialise tout, applique le temps choisi
  // ------------------------------------------------------------------
  nouvellePartie(): void {
    this.arreterHorloge();
    this.tableau.reset();
    this.historique.set([]);
    this.indexAffiche.set(0);
    this.traitBlancs.set(true);
    this.tempsBlancs.set(this.minutesSelectionnees() * 60);
    this.tempsNoirs.set(this.minutesSelectionnees() * 60);
    this.etatPartie.reinitialiser();
    this.reponse.set(null);
    this.erreurAnalyse.set(null);
  }
}
