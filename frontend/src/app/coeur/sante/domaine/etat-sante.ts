// ============================================================================
// Domaine : modele et port pour la verification d'etat du backend
// ============================================================================
// Cette couche ne connait rien de HTTP, d'Angular ni d'aucun framework.
// Elle definit uniquement le contrat (port) que doit respecter tout
// adaptateur d'infrastructure charge d'interroger le backend.

// Representation de l'etat de sante retourne par le backend
export interface EtatSante {
  statut: string;
}

// Port : contrat que doit implementer tout adaptateur de verification
// d'etat, quelle que soit la technologie utilisee (HTTP, WebSocket...)
export interface PortVerificationEtat {
  verifierEtat(): Promise<EtatSante>;
}
