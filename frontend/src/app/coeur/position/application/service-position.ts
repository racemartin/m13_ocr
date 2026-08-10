// ============================================================================
// Cas d'utilisation : interroger la position (theorie, moteur, RAG)
// ============================================================================
// Cette couche orchestre l'appel au port du domaine. Elle ne depend
// d'aucun detail d'infrastructure (HTTP, Angular HttpClient, etc.).
// Un seul port, 4 methodes -- regroupe car les 4 endpoints sont trop
// similaires pour justifier 4 modules hexagonaux distincts.

import { Inject, Injectable } from '@angular/core';

import {
  CoupTheorique,
  Evaluation,
  ExtraitConnaissance,
  PortPositionApi,
  ResultatExploration,
} from '../domaine/modeles';
import { JETON_PORT_POSITION_API } from './jetons';

@Injectable({ providedIn: 'root' })
export class ServicePosition {
  constructor(
    @Inject(JETON_PORT_POSITION_API)
    private readonly port: PortPositionApi,
  ) {}

  async coupsTheoriques(fen: string): Promise<CoupTheorique[]> {
    return this.port.rechercherCoupsTheoriques(fen);
  }

  async evaluation(fen: string): Promise<Evaluation> {
    return this.port.evaluerPosition(fen);
  }

  async exploration(fen: string): Promise<ResultatExploration> {
    return this.port.explorerPosition(fen);
  }

  async contexte(ouverture: string, topK?: number): Promise<ExtraitConnaissance[]> {
    return this.port.rechercherContexte(ouverture, topK);
  }
}
