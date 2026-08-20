// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port agent
// ============================================================================
// CONFIRME (curl direct, 19/08) : le backend (Pydantic/Python) serialise
// bien en snake_case ("coups_theoriques", "nombre_parties", ...). Le
// mappage manuel ci-dessous est donc necessaire et correct -- ne pas le
// supprimer sans revalider par une requete brute (curl) directement
// contre le backend, hors Angular.

import { Injectable }     from '@angular/core';
import { HttpClient }     from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import {
  CoupTheorique, Evaluation, ExtraitConnaissance,
} from '../../position/domaine/modeles';
import { VideoExplicative } from '../../videos/domaine/modeles';
import {
  InfoEco, PortAgentApi, ReponseAgent, ReponseAgentLlm,
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
interface VideoExplicativeBrute {
  id_video: string; titre: string; chaine: string; url: string; vues: number;
}
interface InfoEcoBrut {
  code: string; nom: string; famille: string; categorie: string;
}
interface ReponseAgentBrute {
  fen: string;
  eco: InfoEcoBrut | null;
  coups_theoriques: CoupTheoriqueBrut[];
  evaluation: EvaluationBrute | null;
  contexte_ouverture: ExtraitConnaissanceBrut[];
  videos?: VideoExplicativeBrute[];
  explication?: string | null;
}

@Injectable({ providedIn: 'root' })
export class AdaptateurHttpAgent implements PortAgentApi {
  private readonly urlAgent    = '/api/v1/agent/invoke';
  private readonly urlAgentLlm = '/api/v1/agent-llm/invoke';

  constructor(private readonly http: HttpClient) {}

  async invoquerAgent(fen: string, idSession: string): Promise<ReponseAgent> {
    const brut = await firstValueFrom(
      this.http.post<ReponseAgentBrute>(this.urlAgent, { fen, id_session: idSession }),
    );
    return this.mapperReponse(brut);
  }

  async invoquerAgentLlm(fen: string, idSession: string): Promise<ReponseAgentLlm> {
    const brut = await firstValueFrom(
      this.http.post<ReponseAgentBrute>(this.urlAgentLlm, { fen, id_session: idSession }),
    );
    return {
      ...this.mapperReponse(brut),
      videos: (brut.videos ?? []).map((v) => this.mapperVideo(v)),
      explication: brut.explication ?? '',
    };
  }

  // ------------------------------------------------------------------
  // Mappeurs snake_case (backend) -> camelCase (frontend), explicites
  // ------------------------------------------------------------------
  private mapperReponse(brut: ReponseAgentBrute): ReponseAgent {
    return {
      fen: brut.fen,
      eco: brut.eco ? this.mapperEco(brut.eco) : null,
      coupsTheoriques: brut.coups_theoriques.map((c) => this.mapperCoup(c)),
      evaluation: brut.evaluation ? this.mapperEvaluation(brut.evaluation) : null,
      contexteOuverture: brut.contexte_ouverture.map((e) => this.mapperExtrait(e)),
    };
  }

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

  private mapperVideo(v: VideoExplicativeBrute): VideoExplicative {
    return {
      idVideo: v.id_video, titre: v.titre,
      chaine: v.chaine, url: v.url, vues: v.vues,
    };
  }

  private mapperEco(e: InfoEcoBrut): InfoEco {
    return { code: e.code, nom: e.nom, famille: e.famille, categorie: e.categorie };
  }
}
