// ============================================================================
// Cas d'utilisation : invoquer l'agent (graphe de base ou variante LLM)
// ============================================================================

import { Inject, Injectable } from '@angular/core';

import { PortAgentApi, ReponseAgent, ReponseAgentLlm } from '../domaine/modeles';
import { JETON_PORT_AGENT_API } from './jetons';

@Injectable({ providedIn: 'root' })
export class ServiceAgent {
  constructor(
    @Inject(JETON_PORT_AGENT_API)
    private readonly port: PortAgentApi,
  ) {}

  async analyserPosition(fen: string, idSession: string): Promise<ReponseAgent> {
    return this.port.invoquerAgent(fen, idSession);
  }

  async analyserPositionAvecLlm(fen: string, idSession: string): Promise<ReponseAgentLlm> {
    return this.port.invoquerAgentLlm(fen, idSession);
  }
}
