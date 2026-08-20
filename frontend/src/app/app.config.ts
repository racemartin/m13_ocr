// ============================================================================
// Racine de composition -- SEUL endroit ou un port est relie a son
// adaptateur concret. Equivalent Angular de dependances.py cote backend.
// ============================================================================
// Chaque module definit son propre jeton (coeur/<module>/application/jetons.ts),
// mais ne decide jamais lui-meme quelle implementation le satisfait -- c'est
// la responsabilite exclusive de ce fichier.

import { ApplicationConfig } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';

import { JETON_PORT_VERIFICATION_ETAT } from './coeur/sante/application/jetons';
import { AdaptateurHttpVerificationEtat } from
  './coeur/sante/infrastructure/adaptateur-http-verification-etat';

import { JETON_PORT_POSITION_API } from './coeur/position/application/jetons';
import { AdaptateurHttpPosition } from
  './coeur/position/infrastructure/adaptateur-http-position';

import { JETON_PORT_RECHERCHE_VIDEOS } from './coeur/videos/application/jetons';
import { AdaptateurHttpVideos } from
  './coeur/videos/infrastructure/adaptateur-http-videos';

import { JETON_PORT_AGENT_API } from './coeur/agent/application/jetons';
import { AdaptateurHttpAgent } from
  './coeur/agent/infrastructure/adaptateur-http-agent';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),

    { provide: JETON_PORT_VERIFICATION_ETAT,  useExisting: AdaptateurHttpVerificationEtat },
    { provide: JETON_PORT_POSITION_API,       useExisting: AdaptateurHttpPosition },
    { provide: JETON_PORT_RECHERCHE_VIDEOS,   useExisting: AdaptateurHttpVideos },
    { provide: JETON_PORT_AGENT_API,          useExisting: AdaptateurHttpAgent },
  ],
};
