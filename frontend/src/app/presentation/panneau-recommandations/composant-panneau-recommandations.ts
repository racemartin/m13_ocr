// ============================================================================
// Panneau de recommandations -- affiche la reponse de l'agent (variante LLM)
// ============================================================================

import { Component, Input } from '@angular/core';

import { ReponseAgentLlm } from '../../coeur/agent/domaine/modeles';

@Component({
  selector: 'app-panneau-recommandations',
  standalone: true,
  templateUrl: './composant-panneau-recommandations.html',
  styleUrl: './composant-panneau-recommandations.css',
})
export class ComposantPanneauRecommandations {
  @Input() reponse: ReponseAgentLlm | null = null;
  @Input() enCours = false;
  @Input() erreur: string | null = null;
}
