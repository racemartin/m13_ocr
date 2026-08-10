import { InjectionToken } from '@angular/core';
import { PortPositionApi } from '../domaine/modeles';

export const JETON_PORT_POSITION_API = new InjectionToken<PortPositionApi>(
  'PortPositionApi'
);
