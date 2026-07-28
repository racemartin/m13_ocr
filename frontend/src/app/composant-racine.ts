// ============================================================================
// Composant racine : affiche l'etat de sante du backend (test de cablage)
// ============================================================================
// Ce composant appartient a la couche presentation. Il ne connait que
// le cas d'utilisation (ServiceVerificationEtat), jamais l'adaptateur HTTP
// concret : c'est la configuration "providers" ci-dessous qui relie le
// port a son implementation, seul point de couplage explicite.

import { Component, OnInit } from '@angular/core';
import { HttpClientModule }  from '@angular/common/http';

import { ServiceVerificationEtat } from
  './coeur/sante/application/service-verification-etat';
import { JETON_PORT_VERIFICATION_ETAT } from
  './coeur/sante/application/jetons';
import { AdaptateurHttpVerificationEtat } from
  './coeur/sante/infrastructure/adaptateur-http-verification-etat';

@Component({
  selector    : 'app-racine',
  standalone  : true,
  imports     : [HttpClientModule],
  templateUrl : './composant-racine.html',
  providers   : [
    {
      provide     : JETON_PORT_VERIFICATION_ETAT,
      useExisting : AdaptateurHttpVerificationEtat,
    },
  ],
})
export class ComposantRacine implements OnInit {
  statutBackend = 'en attente...';

  constructor(private readonly service: ServiceVerificationEtat) {}

  ngOnInit(): void {
    this.service
      .verifierEtatBackend()
      .then((etat) => (this.statutBackend = etat.statut))
      .catch(() => (this.statutBackend = 'backend injoignable'));
  }
}
