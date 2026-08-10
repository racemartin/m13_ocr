import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { AdaptateurHttpAgent } from './adaptateur-http-agent';
import { ReponseAgentLlm } from '../domaine/modeles';

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

  it('invoquerAgentLlm() appelle POST /api/v1/agent-llm/invoke avec fen + id_session', async () => {
    const reponseAttendue: ReponseAgentLlm = {
      fen: 'abc', coupsTheoriques: [], evaluation: null, contexteOuverture: [],
      videos: [], explication: 'test',
    };
    const promesse = adaptateur.invoquerAgentLlm('abc', 'session-1');

    const requete = httpMock.expectOne('/api/v1/agent-llm/invoke');
    expect(requete.request.method).toBe('POST');
    expect(requete.request.body).toEqual({ fen: 'abc', id_session: 'session-1' });
    requete.flush(reponseAttendue);

    expect(await promesse).toEqual(reponseAttendue);
  });
});
