// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port videos
// ============================================================================

import { Injectable }     from '@angular/core';
import { HttpClient }     from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { PortRechercheVideos, VideoExplicative } from '../domaine/modeles';

@Injectable({ providedIn: 'root' })
export class AdaptateurHttpVideos implements PortRechercheVideos {
  private readonly url = '/api/v1/videos';

  constructor(private readonly http: HttpClient) {}

  async rechercherVideos(ouverture: string): Promise<VideoExplicative[]> {
    return firstValueFrom(
      this.http.get<VideoExplicative[]>(`${this.url}/${encodeURIComponent(ouverture)}`),
    );
  }
}
