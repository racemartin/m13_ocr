// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port de position
// ============================================================================
// IMPORTANT : le backend (Pydantic/Python) serialise en snake_case, et pour
// Evaluation dans une structure imbriquee differente du type plat cote
// frontend -- ce fichier fait EXPLICITEMENT la conversion, champ par champ.
// Sans ca, TypeScript accepte silencieusement le cast (aucune verification
// a l'execution) -- bug reel rencontre en production sur agent-llm/invoke,
// meme cause ici.

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

// -- Formes brutes telles qu'elles arrivent reellement du backend --------
interface CoupTheoriqueBrut {
  uci: string; san: string; nombre_parties: number;
}
interface EvaluationBrute {
  fen: string;
  evaluation: { type: string; value: number; score: string };
  best_move: string | null;
  depth: number;
}
interface ExtraitConnaissanceBrut {
  texte: string; ouverture: string; source_url: string; score: number;
}
// /explore renvoie une UNION : soit la theorie, soit l'evaluation --
// jamais les deux en meme temps (discrimine par "type").
type ExplorationBrute =
  | { fen: string; type: 'theorie'; coups: CoupTheoriqueBrut[] }
  | (EvaluationBrute & { type: 'evaluation' });

@Injectable({ providedIn: 'root' })
export class AdaptateurHttpPosition implements PortPositionApi {
  private readonly urlMoves        = '/api/v1/moves';
  private readonly urlEvaluate     = '/api/v1/evaluate';
  private readonly urlExplore      = '/api/v1/explore';
  private readonly urlVectorSearch = '/api/v1/vector-search';

  constructor(private readonly http: HttpClient) {}

  async rechercherCoupsTheoriques(fen: string): Promise<CoupTheorique[]> {
    const brut = await firstValueFrom(
      this.http.get<CoupTheoriqueBrut[]>(`${this.urlMoves}/${encodeURIComponent(fen)}`),
    );
    return brut.map((c) => this.mapperCoup(c));
  }

  async evaluerPosition(fen: string): Promise<Evaluation> {
    const brut = await firstValueFrom(
      this.http.get<EvaluationBrute>(`${this.urlEvaluate}/${encodeURIComponent(fen)}`),
    );
    return this.mapperEvaluation(brut);
  }

  async explorerPosition(fen: string): Promise<ResultatExploration> {
    const brut = await firstValueFrom(
      this.http.get<ExplorationBrute>(`${this.urlExplore}/${encodeURIComponent(fen)}`),
    );
    if (brut.type === 'theorie') {
      return {
        type: 'theorie',
        coups: brut.coups.map((c) => this.mapperCoup(c)),
        evaluation: null,
      };
    }
    return {
      type: 'evaluation',
      coups: [],
      evaluation: this.mapperEvaluation(brut),
    };
  }

  async rechercherContexte(ouverture: string, topK?: number): Promise<ExtraitConnaissance[]> {
    let params = new HttpParams().set('q', ouverture);
    if (topK !== undefined) {
      params = params.set('top_k', topK);
    }
    const brut = await firstValueFrom(
      this.http.get<ExtraitConnaissanceBrut[]>(this.urlVectorSearch, { params }),
    );
    return brut.map((e) => this.mapperExtrait(e));
  }

  // ------------------------------------------------------------------
  // Mappeurs snake_case (backend) -> camelCase (frontend), explicites
  // ------------------------------------------------------------------
  private mapperCoup(c: CoupTheoriqueBrut): CoupTheorique {
    return { uci: c.uci, san: c.san, nombreParties: c.nombre_parties };
  }

  private mapperEvaluation(e: EvaluationBrute): Evaluation {
    return {
      type: e.evaluation.type,
      valeur: e.evaluation.value,
      coupRecommande: e.best_move ?? '',
      profondeur: e.depth,
    };
  }

  private mapperExtrait(e: ExtraitConnaissanceBrut): ExtraitConnaissance {
    return {
      texte: e.texte, ouverture: e.ouverture,
      sourceUrl: e.source_url, score: e.score,
    };
  }
}
