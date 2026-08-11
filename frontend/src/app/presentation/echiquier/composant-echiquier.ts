// ============================================================================
// Echiquier interactif -- ngx-chess-board + ServiceEtatPartie + ServiceAgent
// ============================================================================

import { Component, signal, ViewChild } from '@angular/core';
import { NgxChessBoardModule, NgxChessBoardView } from 'ngx-chess-board';

import { ServiceEtatPartie } from '../../coeur/partie/application/service-etat-partie';
import { ServiceAgent } from '../../coeur/agent/application/service-agent';
import { ReponseAgentLlm } from '../../coeur/agent/domaine/modeles';
import { ComposantPanneauRecommandations } from
  '../panneau-recommandations/composant-panneau-recommandations';

@Component({
  selector: 'app-echiquier',
  standalone: true,
  imports: [NgxChessBoardModule, ComposantPanneauRecommandations],
  templateUrl: './composant-echiquier.html',
  styleUrl: './composant-echiquier.css',
})
export class ComposantEchiquier {
  @ViewChild('tableau', { static: false }) tableau!: NgxChessBoardView;

  reponse = signal<ReponseAgentLlm | null>(null);
  enCours = signal(false);
  erreur = signal<string | null>(null);

  constructor(
    private readonly etatPartie: ServiceEtatPartie,
    private readonly serviceAgent: ServiceAgent,
  ) {}

  async surCoupJoue(): Promise<void> {
    const fen = this.tableau.getFEN();
    this.etatPartie.definirFen(fen);

    this.enCours.set(true);
    this.erreur.set(null);

    try {
      const reponse = await this.serviceAgent.analyserPositionAvecLlm(
        fen, this.etatPartie.idSession(),
      );
      this.reponse.set(reponse);
    } catch (e) {
      this.erreur.set(e instanceof Error ? e.message : String(e));
    } finally {
      this.enCours.set(false);
    }
  }

  reinitialiser(): void {
    this.tableau.reset();
    this.etatPartie.reinitialiser();
    this.reponse.set(null);
    this.erreur.set(null);
  }
}
