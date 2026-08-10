import { InjectionToken } from '@angular/core';
import { PortRechercheVideos } from '../domaine/modeles';

export const JETON_PORT_RECHERCHE_VIDEOS = new InjectionToken<PortRechercheVideos>(
  'PortRechercheVideos'
);
