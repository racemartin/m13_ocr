// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port videos
// ============================================================================
// Le backend serialise id_video (snake_case) -- mappage explicite vers
// idVideo, meme raison que les autres adaptateurs (cf. leurs commentaires).
import { Injectable }     from '@angular/core';
import { HttpClient }     from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { PortRechercheVideos, VideoExplicative } from '../domaine/modeles';
interface VideoExplicativeBrute {
  id_video: string; titre: string; chaine: string; url: string; vues: number;
}
@Injectable({ providedIn: 'root' })
export class AdaptateurHttpVideos implements PortRechercheVideos {
  private readonly url = '/api/v1/videos';
  constructor(private readonly http: HttpClient) {}
  async rechercherVideos(ouverture: string): Promise<VideoExplicative[]> {
    const brut = await firstValueFrom(
      this.http.get<VideoExplicativeBrute[]>(`${this.url}/${encodeURIComponent(ouverture)}`),
    );
    return brut.map((v) => ({
      idVideo: v.id_video, titre: v.titre,
      chaine: v.chaine, url: v.url, vues: v.vues,
    }));
  }
}
