// ============================================================================
// Tests : AdaptateurHttpPosition
// ============================================================================
// Verifie que l'adaptateur construit les bonnes URLs et transmet la reponse
// telle quelle -- aucun appel reseau reel (HttpClientTestingModule).

import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { AdaptateurHttpPosition } from './adaptateur-http-position';
import { CoupTheorique, Evaluation } from '../domaine/modeles';

describe('AdaptateurHttpPosition', () => {
  let adaptateur: AdaptateurHttpPosition;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        AdaptateurHttpPosition,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    adaptateur = TestBed.inject(AdaptateurHttpPosition);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('rechercherCoupsTheoriques() appelle GET /api/v1/moves/{fen}', async () => {
    const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    const reponseAttendue: CoupTheorique[] = [
      { uci: 'e2e4', san: 'e4', nombreParties: 1 },
    ];

    const promesse = adaptateur.rechercherCoupsTheoriques(fen);

    const requete = httpMock.expectOne(
      (r) => r.url === `/api/v1/moves/${encodeURIComponent(fen)}`,
    );
    expect(requete.request.method).toBe('GET');
    requete.flush(reponseAttendue);

    expect(await promesse).toEqual(reponseAttendue);
  });

  it('evaluerPosition() appelle GET /api/v1/evaluate/{fen}', async () => {
    const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    const reponseAttendue: Evaluation = {
      type: 'cp', valeur: 39, coupRecommande: 'e2e4', profondeur: 15,
    };

    const promesse = adaptateur.evaluerPosition(fen);

    const requete = httpMock.expectOne(
      (r) => r.url === `/api/v1/evaluate/${encodeURIComponent(fen)}`,
    );
    requete.flush(reponseAttendue);

    expect(await promesse).toEqual(reponseAttendue);
  });

  it('rechercherContexte() envoie q et top_k en query params', async () => {
    const promesse = adaptateur.rechercherContexte('Sicilienne', 3);

    const requete = httpMock.expectOne(
      (r) => r.url === '/api/v1/vector-search'
        && r.params.get('q') === 'Sicilienne'
        && r.params.get('top_k') === '3',
    );
    requete.flush([]);

    expect(await promesse).toEqual([]);
  });
});
