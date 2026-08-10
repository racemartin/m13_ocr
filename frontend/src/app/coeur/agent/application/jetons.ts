import { InjectionToken } from '@angular/core';
import { PortAgentApi } from '../domaine/modeles';

export const JETON_PORT_AGENT_API = new InjectionToken<PortAgentApi>('PortAgentApi');
