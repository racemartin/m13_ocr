// ============================================================================
// Etat partage du plateau (FEN) -- signal Angular, pas de port/adaptateur
// ============================================================================
// Delibere : cet etat est 100% local au navigateur, aucun systeme externe
// a abstraire derriere un port. Partage entre l'echiquier et le futur
// panel Admin (qui peut le surcharger sans modifier l'etat reel du jeu).

import { Injectable, signal } from '@angular/core';

const FEN_POSITION_INITIALE =
  'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

@Injectable({ providedIn: 'root' })
export class ServiceEtatPartie {
  private readonly _fen = signal(FEN_POSITION_INITIALE);
  private readonly _idSession = signal(this.genererIdSession());

  readonly fen = this._fen.asReadonly();
  readonly idSession = this._idSession.asReadonly();

  definirFen(fen: string): void {
    this._fen.set(fen);
  }

  reinitialiser(): void {
    this._fen.set(FEN_POSITION_INITIALE);
  }

  private genererIdSession(): string {
    return `partie-${Date.now()}`;
  }
}
