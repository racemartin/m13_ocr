// ============================================================================
// Adaptateur d'infrastructure : implementation HTTP du port de sante
// ============================================================================
// Seul cet adaptateur connait l'URL et le format HTTP de l'API. Si demain
// on change de backend ou de protocole, seul ce fichier est modifie.

import { Injectable }     from '@angular/core';
import { HttpClient }     from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

import { EtatSante, PortVerificationEtat } from '../domaine/etat-sante';

@Injectable({ providedIn: 'root' })
export class AdaptateurHttpVerificationEtat implements PortVerificationEtat {
  // Chemin relatif : passe par le reverse proxy Nginx (/api/ -> backend)
  private readonly url = '/api/v1/healthcheck';

  constructor(private readonly http: HttpClient) {}

  async verifierEtat(): Promise<EtatSante> {
    return firstValueFrom(this.http.get<EtatSante>(this.url));
  }
}
