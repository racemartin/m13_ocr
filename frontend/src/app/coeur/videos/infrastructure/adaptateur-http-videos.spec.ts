import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

import { AdaptateurHttpVideos } from './adaptateur-http-videos';
import { VideoExplicative } from '../domaine/modeles';

describe('AdaptateurHttpVideos', () => {
  let adaptateur: AdaptateurHttpVideos;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AdaptateurHttpVideos, provideHttpClient(), provideHttpClientTesting()],
    });
    adaptateur = TestBed.inject(AdaptateurHttpVideos);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('rechercherVideos() appelle GET /api/v1/videos/{ouverture}', async () => {
    const reponseAttendue: VideoExplicative[] = [
      { idVideo: 'abc', titre: 'Sicilienne', chaine: 'GothamChess', url: 'https://youtube.com/x', vues: 1000 },
    ];
    const promesse = adaptateur.rechercherVideos('Sicilienne');

    const requete = httpMock.expectOne('/api/v1/videos/Sicilienne');
    expect(requete.request.method).toBe('GET');
    requete.flush(reponseAttendue);

    expect(await promesse).toEqual(reponseAttendue);
  });
});
