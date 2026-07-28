// Jeton d'injection Angular pour le port de verification d'etat.
// Permet a la couche application de rester independante de
// l'implementation concrete (adaptateur HTTP, mock de test, etc.).
import { InjectionToken } from '@angular/core';

import { PortVerificationEtat } from '../domaine/etat-sante';

export const JETON_PORT_VERIFICATION_ETAT =
  new InjectionToken<PortVerificationEtat>('PortVerificationEtat');
