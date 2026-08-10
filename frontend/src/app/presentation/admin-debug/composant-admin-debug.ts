// ============================================================================
// Panel Admin/Debug -- teste les 8 endpoints reels, style Insomnia integre
// ============================================================================
// Ne duplique AUCUNE logique d'appel : reutilise les memes 4 services que
// le reste de l'application (ServiceVerificationEtat, ServicePosition,
// ServiceVideos, ServiceAgent). Un bug vu ici est un bug reel de l'app.

import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ServiceVerificationEtat } from
  '../../coeur/sante/application/service-verification-etat';
import { ServicePosition } from
  '../../coeur/position/application/service-position';
import { ServiceVideos } from
  '../../coeur/videos/application/service-videos';
import { ServiceAgent } from
  '../../coeur/agent/application/service-agent';

interface DescripteurEndpoint {
  id: string;
  groupe: string;
  methode: 'GET' | 'POST';
  libelle: string;
  requis: ('fen' | 'ouverture' | 'idSession')[];
  executer: () => Promise<unknown>;
}

@Component({
  selector: 'app-admin-debug',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './composant-admin-debug.html',
  styleUrl: './composant-admin-debug.css',
})
export class ComposantAdminDebug {
  // -- Champs du formulaire de parametres (partages par tous les endpoints) --
  fen = signal(
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
  );
  ouverture = signal('Espagnole');
  topK = signal<number | null>(3);
  idSession = signal('demo-admin-1');

  // -- Etat de la derniere requete --
  endpointSelectionne = signal<string | null>(null);
  enCours = signal(false);
  statutHttp = signal<string | null>(null);
  dureeMs = signal<number | null>(null);
  reponseBrute = signal<string>('');
  erreur = signal<string | null>(null);

  constructor(
    private readonly serviceSante: ServiceVerificationEtat,
    private readonly servicePosition: ServicePosition,
    private readonly serviceVideos: ServiceVideos,
    private readonly serviceAgent: ServiceAgent,
  ) {}

  readonly registreEndpoints: DescripteurEndpoint[] = [
    {
      id: 'healthcheck', groupe: 'Sante', methode: 'GET',
      libelle: 'GET /healthcheck', requis: [],
      executer: () => this.serviceSante.verifierEtatBackend(),
    },
    {
      id: 'moves', groupe: 'Position', methode: 'GET',
      libelle: 'GET /moves/{fen}', requis: ['fen'],
      executer: () => this.servicePosition.coupsTheoriques(this.fen()),
    },
    {
      id: 'evaluate', groupe: 'Position', methode: 'GET',
      libelle: 'GET /evaluate/{fen}', requis: ['fen'],
      executer: () => this.servicePosition.evaluation(this.fen()),
    },
    {
      id: 'explore', groupe: 'Position', methode: 'GET',
      libelle: 'GET /explore/{fen}', requis: ['fen'],
      executer: () => this.servicePosition.exploration(this.fen()),
    },
    {
      id: 'vector-search', groupe: 'Position', methode: 'GET',
      libelle: 'GET /vector-search', requis: ['ouverture'],
      executer: () => this.servicePosition.contexte(
        this.ouverture(), this.topK() ?? undefined,
      ),
    },
    {
      id: 'videos', groupe: 'Videos', methode: 'GET',
      libelle: 'GET /videos/{ouverture}', requis: ['ouverture'],
      executer: () => this.serviceVideos.rechercher(this.ouverture()),
    },
    {
      id: 'agent-invoke', groupe: 'Agent', methode: 'POST',
      libelle: 'POST /agent/invoke', requis: ['fen', 'idSession'],
      executer: () => this.serviceAgent.analyserPosition(this.fen(), this.idSession()),
    },
    {
      id: 'agent-llm-invoke', groupe: 'Agent', methode: 'POST',
      libelle: 'POST /agent-llm/invoke', requis: ['fen', 'idSession'],
      executer: () => this.serviceAgent.analyserPositionAvecLlm(this.fen(), this.idSession()),
    },
  ];

  champManquant(descripteur: DescripteurEndpoint): string | null {
    for (const champ of descripteur.requis) {
      if (champ === 'fen' && !this.fen().trim()) return 'fen';
      if (champ === 'ouverture' && !this.ouverture().trim()) return 'ouverture';
      if (champ === 'idSession' && !this.idSession().trim()) return 'id-session';
    }
    return null;
  }

  async declencherAppel(descripteur: DescripteurEndpoint): Promise<void> {
    const manquant = this.champManquant(descripteur);
    if (manquant) {
      this.erreur.set(`Champ requis manquant : ${manquant}`);
      return;
    }

    this.endpointSelectionne.set(descripteur.id);
    this.enCours.set(true);
    this.erreur.set(null);
    this.statutHttp.set(null);
    this.reponseBrute.set('');

    const debut = performance.now();
    try {
      const reponse = await descripteur.executer();
      this.dureeMs.set(Math.round(performance.now() - debut));
      this.statutHttp.set('200 OK');
      this.reponseBrute.set(JSON.stringify(reponse, null, 2));
    } catch (e) {
      this.dureeMs.set(Math.round(performance.now() - debut));
      this.statutHttp.set('Erreur');
      this.erreur.set(e instanceof Error ? e.message : String(e));
    } finally {
      this.enCours.set(false);
    }
  }

  groupes(): string[] {
    return [...new Set(this.registreEndpoints.map((d) => d.groupe))];
  }

  endpointsDuGroupe(groupe: string): DescripteurEndpoint[] {
    return this.registreEndpoints.filter((d) => d.groupe === groupe);
  }
}
