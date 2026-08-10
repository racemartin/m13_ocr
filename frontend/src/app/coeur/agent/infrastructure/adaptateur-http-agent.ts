// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port agent
// ============================================================================

import { Injectable }     from '@angular/core';
import { HttpClient }     from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { PortAgentApi, ReponseAgent, ReponseAgentLlm } from '../domaine/modeles';

@Injectable({ providedIn: 'root' })
export class AdaptateurHttpAgent implements PortAgentApi {
  private readonly urlAgent    = '/api/v1/agent/invoke';
  private readonly urlAgentLlm = '/api/v1/agent-llm/invoke';

  constructor(private readonly http: HttpClient) {}

  async invoquerAgent(fen: string, idSession: string): Promise<ReponseAgent> {
    return firstValueFrom(
      this.http.post<ReponseAgent>(this.urlAgent, { fen, id_session: idSession }),
    );
  }

  async invoquerAgentLlm(fen: string, idSession: string): Promise<ReponseAgentLlm> {
    return firstValueFrom(
      this.http.post<ReponseAgentLlm>(this.urlAgentLlm, { fen, id_session: idSession }),
    );
  }
}
