// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port de position
// ============================================================================
// Seul cet adaptateur connait les URLs et le format HTTP de l'API. Si demain
// on change de backend ou de protocole, seul ce fichier est modifie.

import { Injectable }     from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import {
  CoupTheorique,
  Evaluation,
  ExtraitConnaissance,
  PortPositionApi,
  ResultatExploration,
} from '../domaine/modeles';

@Injectable({ providedIn: 'root' })
export class AdaptateurHttpPosition implements PortPositionApi {
  // Chemins relatifs : passent par le reverse proxy Nginx (/api/ -> backend)
  private readonly urlMoves        = '/api/v1/moves';
  private readonly urlEvaluate     = '/api/v1/evaluate';
  private readonly urlExplore      = '/api/v1/explore';
  private readonly urlVectorSearch = '/api/v1/vector-search';

  constructor(private readonly http: HttpClient) {}

  async rechercherCoupsTheoriques(fen: string): Promise<CoupTheorique[]> {
    return firstValueFrom(
      this.http.get<CoupTheorique[]>(`${this.urlMoves}/${encodeURIComponent(fen)}`),
    );
  }

  async evaluerPosition(fen: string): Promise<Evaluation> {
    return firstValueFrom(
      this.http.get<Evaluation>(`${this.urlEvaluate}/${encodeURIComponent(fen)}`),
    );
  }

  async explorerPosition(fen: string): Promise<ResultatExploration> {
    return firstValueFrom(
      this.http.get<ResultatExploration>(`${this.urlExplore}/${encodeURIComponent(fen)}`),
    );
  }

  async rechercherContexte(ouverture: string, topK?: number): Promise<ExtraitConnaissance[]> {
    let params = new HttpParams().set('q', ouverture);
    if (topK !== undefined) {
      params = params.set('top_k', topK);
    }
    return firstValueFrom(
      this.http.get<ExtraitConnaissance[]>(this.urlVectorSearch, { params }),
    );
  }
}
