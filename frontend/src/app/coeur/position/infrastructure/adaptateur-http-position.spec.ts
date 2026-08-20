import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { AdaptateurHttpPosition } from './adaptateur-http-position';

describe('AdaptateurHttpPosition', () => {
  let adaptateur: AdaptateurHttpPosition;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AdaptateurHttpPosition, provideHttpClient(), provideHttpClientTesting()],
    });
    adaptateur = TestBed.inject(AdaptateurHttpPosition);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('rechercherCoupsTheoriques() mappe nombre_parties -> nombreParties (JSON reel)', async () => {
    const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    const corpsReelDuBackend = [{ uci: 'e2e4', san: 'e4', nombre_parties: 1 }];

    const promesse = adaptateur.rechercherCoupsTheoriques(fen);

    const requete = httpMock.expectOne(
      (r) => r.url === `/api/v1/moves/${encodeURIComponent(fen)}`,
    );
    expect(requete.request.method).toBe('GET');
    requete.flush(corpsReelDuBackend);

    const resultat = await promesse;
    expect(resultat[0].nombreParties).toBe(1);
  });

  it('evaluerPosition() aplatit la structure imbriquee reelle du backend', async () => {
    const fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
    const corpsReelDuBackend = {
      fen, evaluation: { type: 'cp', value: 39, score: '+0.39' },
      best_move: 'e2e4', depth: 15,
    };

    const promesse = adaptateur.evaluerPosition(fen);
    httpMock.expectOne(
      (r) => r.url === `/api/v1/evaluate/${encodeURIComponent(fen)}`,
    ).flush(corpsReelDuBackend);

    const resultat = await promesse;
    expect(resultat).toEqual({
      type: 'cp', valeur: 39, coupRecommande: 'e2e4', profondeur: 15,
    });
  });

  it('explorerPosition() gere la branche "theorie" de l\'union reelle', async () => {
    const fen = 'abc';
    const corpsTheorie = {
      fen, type: 'theorie', coups: [{ uci: 'e2e4', san: 'e4', nombre_parties: 1 }],
    };

    const promesse = adaptateur.explorerPosition(fen);
    httpMock.expectOne(
      (r) => r.url === `/api/v1/explore/${encodeURIComponent(fen)}`,
    ).flush(corpsTheorie);

    const resultat = await promesse;
    expect(resultat.type).toBe('theorie');
    expect(resultat.coups[0].nombreParties).toBe(1);
    expect(resultat.evaluation).toBeNull();
  });

  it('explorerPosition() gere la branche "evaluation" de l\'union reelle', async () => {
    const fen = 'abc';
    const corpsEvaluation = {
      fen, type: 'evaluation',
      evaluation: { type: 'cp', value: 10, score: '+0.10' },
      best_move: 'd2d4', depth: 12,
    };

    const promesse = adaptateur.explorerPosition(fen);
    httpMock.expectOne(
      (r) => r.url === `/api/v1/explore/${encodeURIComponent(fen)}`,
    ).flush(corpsEvaluation);

    const resultat = await promesse;
    expect(resultat.type).toBe('evaluation');
    expect(resultat.coups).toEqual([]);
    expect(resultat.evaluation).toEqual({
      type: 'cp', valeur: 10, coupRecommande: 'd2d4', profondeur: 12,
    });
  });

  it('rechercherContexte() mappe source_url -> sourceUrl (JSON reel)', async () => {
    const corpsReelDuBackend = [
      { texte: '...', ouverture: 'Sicilienne', source_url: 'https://fr.wikipedia.org/x', score: 0.9 },
    ];

    const promesse = adaptateur.rechercherContexte('Sicilienne', 3);

    const requete = httpMock.expectOne(
      (r) => r.url === '/api/v1/vector-search'
        && r.params.get('q') === 'Sicilienne'
        && r.params.get('top_k') === '3',
    );
    requete.flush(corpsReelDuBackend);

    const resultat = await promesse;
    expect(resultat[0].sourceUrl).toBe('https://fr.wikipedia.org/x');
  });
});
