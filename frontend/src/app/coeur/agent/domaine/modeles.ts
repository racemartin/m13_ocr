import { CoupTheorique } from '../../position/domaine/modeles';
import { VideoExplicative } from '../../videos/domaine/modeles';

export interface ReponseAgent {
  fen: string;
  coupsTheoriques: CoupTheorique[];
  evaluation: unknown;
  contexteOuverture: unknown[];
}

export interface ReponseAgentLlm extends ReponseAgent {
  videos: VideoExplicative[];
  explication: string;
}

export interface PortAgentApi {
  invoquerAgent(fen: string, idSession: string): Promise<ReponseAgent>;
  invoquerAgentLlm(fen: string, idSession: string): Promise<ReponseAgentLlm>;
}
