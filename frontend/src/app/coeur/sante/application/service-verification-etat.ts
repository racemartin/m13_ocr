// ============================================================================
// Cas d'utilisation : verifier l'etat de sante du backend
// ============================================================================
// Cette couche orchestre l'appel au port du domaine. Elle ne depend
// d'aucun detail d'infrastructure (HTTP, Angular HttpClient, etc.).

import { Inject, Injectable } from '@angular/core';

import { EtatSante, PortVerificationEtat } from '../domaine/etat-sante';
import { JETON_PORT_VERIFICATION_ETAT } from './jetons';

@Injectable({ providedIn: 'root' })
export class ServiceVerificationEtat {
  constructor(
    @Inject(JETON_PORT_VERIFICATION_ETAT)
    private readonly port: PortVerificationEtat,
  ) {}

  // Execute le cas d'utilisation : interroge le backend via le port
  async verifierEtatBackend(): Promise<EtatSante> {
    return this.port.verifierEtat();
  }
}
