import { CoupTheorique, Evaluation, ExtraitConnaissance } from '../../position/domaine/modeles';
import { VideoExplicative } from '../../videos/domaine/modeles';

export interface InfoEco {
  code      : string;
  nom       : string;
  famille   : string;
  categorie : string;
}

export interface ReponseAgent {
  fen               : string;
  eco               : InfoEco | null;
  coupsTheoriques   : CoupTheorique[];
  evaluation        : Evaluation | null;
  contexteOuverture : ExtraitConnaissance[];
}

export interface ReponseAgentLlm extends ReponseAgent {
  videos      : VideoExplicative[];
  explication : string;
}

export interface PortAgentApi {
  invoquerAgent(fen: string, idSession: string): Promise<ReponseAgent>;
  invoquerAgentLlm(fen: string, idSession: string): Promise<ReponseAgentLlm>;
}
