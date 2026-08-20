import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { AdaptateurHttpAgent } from './adaptateur-http-agent';

describe('AdaptateurHttpAgent', () => {
  let adaptateur: AdaptateurHttpAgent;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AdaptateurHttpAgent, provideHttpClient(), provideHttpClientTesting()],
    });
    adaptateur = TestBed.inject(AdaptateurHttpAgent);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('invoquerAgentLlm() mappe correctement le JSON reel (snake_case) du backend', async () => {
    // Forme EXACTE renvoyee par le vrai backend (Pydantic) -- pas la
    // forme deja traduite en camelCase. Sans ce test avec un corps
    // realiste, un bug de mappage passe inapercu (deja arrive en prod).
    const corpsReelDuBackend = {
      fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
      eco: { code: 'B20', nom: 'Sicilian Defense', famille: 'Sicilian Defense', categorie: 'Jeux semi-ouverts' },
      coups_theoriques: [{ uci: 'e2e4', san: 'e4', nombre_parties: 125000 }],
      evaluation: null,
      contexte_ouverture: [
        { texte: '...', ouverture: 'Sicilienne', source_url: 'https://fr.wikipedia.org/...', score: 0.9 },
      ],
      videos: [
        { id_video: 'abc123', titre: 'Titre video', chaine: 'GothamChess', url: 'https://youtube.com/x', vues: 1000 },
      ],
      explication: 'Explication pedagogique.',
    };

    const promesse = adaptateur.invoquerAgentLlm('abc', 'session-1');

    const requete = httpMock.expectOne('/api/v1/agent-llm/invoke');
    expect(requete.request.method).toBe('POST');
    expect(requete.request.body).toEqual({ fen: 'abc', id_session: 'session-1' });
    requete.flush(corpsReelDuBackend);

    const resultat = await promesse;

    // Verifie que le mappage snake_case -> camelCase a bien eu lieu
    expect(resultat.coupsTheoriques[0].nombreParties).toBe(125000);
    expect(resultat.contexteOuverture[0].sourceUrl).toBe('https://fr.wikipedia.org/...');
    expect(resultat.videos[0].idVideo).toBe('abc123');
    expect(resultat.eco?.famille).toBe('Sicilian Defense');
  });

  it('invoquerAgentLlm() aplatit correctement la structure imbriquee de evaluation', async () => {
    const corpsAvecEvaluation = {
      fen: 'abc',
      eco: null,
      coups_theoriques: [],
      evaluation: {
        fen: 'abc',
        evaluation: { type: 'cp', value: 39, score: '+0.39' },
        best_move: 'e2e4',
        depth: 15,
      },
      contexte_ouverture: [],
      videos: [],
      explication: null,
    };

    const promesse = adaptateur.invoquerAgentLlm('abc', 'session-1');
    httpMock.expectOne('/api/v1/agent-llm/invoke').flush(corpsAvecEvaluation);
    const resultat = await promesse;

    expect(resultat.evaluation).toEqual({
      type: 'cp', valeur: 39, coupRecommande: 'e2e4', profondeur: 15,
    });
  });
});
