// ============================================================================
// Cas d'utilisation : rechercher des videos explicatives pour une ouverture
// ============================================================================

import { Inject, Injectable } from '@angular/core';

import { PortRechercheVideos, VideoExplicative } from '../domaine/modeles';
import { JETON_PORT_RECHERCHE_VIDEOS } from './jetons';

@Injectable({ providedIn: 'root' })
export class ServiceVideos {
  constructor(
    @Inject(JETON_PORT_RECHERCHE_VIDEOS)
    private readonly port: PortRechercheVideos,
  ) {}

  async rechercher(ouverture: string): Promise<VideoExplicative[]> {
    return this.port.rechercherVideos(ouverture);
  }
}
