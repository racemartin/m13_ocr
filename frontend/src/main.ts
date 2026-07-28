// Point d'entree de l'application Angular (bootstrap standalone)
import { bootstrapApplication } from '@angular/platform-browser';

import { ComposantRacine } from './app/composant-racine';

bootstrapApplication(ComposantRacine).catch((erreur) =>
  console.error(erreur),
);
