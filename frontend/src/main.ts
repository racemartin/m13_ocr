// Point d'entree de l'application Angular (bootstrap standalone)
import { bootstrapApplication } from '@angular/platform-browser';

import { appConfig } from './app/app.config';
import { ComposantRacine } from './app/composant-racine';

bootstrapApplication(ComposantRacine, appConfig).catch((erreur) =>
  console.error(erreur),
);
