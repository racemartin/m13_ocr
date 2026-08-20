// ============================================================================
// Panneau de recommandations -- affiche la reponse de l'agent (variante LLM)
// ============================================================================
// Les coups theoriques ET les coups mentionnes en gras dans le texte libre
// (ex. "**e2e3**") sont cliquables -- emet jouerCoup vers ComposantEchiquier,
// qui est seul a detenir la reference au plateau (@ViewChild).

import { Component, EventEmitter, Input, Output } from '@angular/core';

import { ReponseAgentLlm } from '../../coeur/agent/domaine/modeles';

type SegmentExplication =
  | { type: 'texte'; texte: string }
  | { type: 'gras'; texte: string }
  | { type: 'coup'; texte: string };    // texte = coup au format UCI (ex. "e2e3")

// Coordonnees UCI : case de depart + case d'arrivee, promotion optionnelle
// (ex. "e2e4", "e7e8q"). Ne detecte PAS la notation algebrique standard
// ("Nf3", "Cxe5"...) -- cf. limite documentee dans la reponse au chat.
const MOTIF_UCI = /^[a-h][1-8][a-h][1-8][qrbn]?$/i;

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

  @Output() jouerCoup = new EventEmitter<string>();

  // ------------------------------------------------------------------
  // Decoupe reponse.explication en segments texte / gras / coup-jouable,
  // en repartant des marqueurs Markdown **...** generes par le LLM.
  // ------------------------------------------------------------------
  segmentsExplication(): SegmentExplication[] {
    const explication = this.reponse?.explication ?? '';
    const segments: SegmentExplication[] = [];
    const motifGras = /\*\*(.+?)\*\*/g;
    let dernierIndex = 0;
    let correspondance: RegExpExecArray | null;

    while ((correspondance = motifGras.exec(explication)) !== null) {
      if (correspondance.index > dernierIndex) {
        segments.push({
          type: 'texte',
          texte: explication.slice(dernierIndex, correspondance.index),
        });
      }
      const contenu = correspondance[1].trim();
      segments.push({
        type: MOTIF_UCI.test(contenu) ? 'coup' : 'gras',
        texte: contenu,
      });
      dernierIndex = motifGras.lastIndex;
    }
    if (dernierIndex < explication.length) {
      segments.push({ type: 'texte', texte: explication.slice(dernierIndex) });
    }
    return segments;
  }
}
