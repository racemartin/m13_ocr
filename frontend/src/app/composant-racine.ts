// ============================================================================
// Composant racine : menu lateral (Admin / Echiquier) + zone de contenu
// ============================================================================
// Simple bascule par signal -- pas besoin d'Angular Router pour 2 onglets.

import { Component, signal } from '@angular/core';

import { ComposantAdminDebug } from './presentation/admin-debug/composant-admin-debug';
import { ComposantEchiquier }  from './presentation/echiquier/composant-echiquier';

type Vue = 'admin' | 'echiquier';

@Component({
  selector: 'app-racine',
  standalone: true,
  imports: [ComposantAdminDebug, ComposantEchiquier],
  templateUrl: './composant-racine.html',
  styleUrl: './composant-racine.css',
})
export class ComposantRacine {
  vueActive = signal<Vue>('admin');

  choisirVue(vue: Vue): void {
    this.vueActive.set(vue);
  }
}
