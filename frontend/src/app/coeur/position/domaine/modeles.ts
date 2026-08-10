export interface CoupTheorique {
  uci: string;
  san: string;
  nombreParties: number;
}

export interface Evaluation {
  type: string;
  valeur: number;
  coupRecommande: string;
  profondeur: number;
}

export interface ExtraitConnaissance {
  texte: string;
  ouverture: string;
  sourceUrl: string;
  score: number;
}

export interface ResultatExploration {
  type: string;
  coups: CoupTheorique[];
  evaluation: Evaluation | null;
}

export interface PortPositionApi {
  rechercherCoupsTheoriques(fen: string): Promise<CoupTheorique[]>;
  evaluerPosition(fen: string): Promise<Evaluation>;
  explorerPosition(fen: string): Promise<ResultatExploration>;
  rechercherContexte(ouverture: string, topK?: number): Promise<ExtraitConnaissance[]>;
}
