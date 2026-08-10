export interface VideoExplicative {
  idVideo: string;
  titre: string;
  chaine: string;
  url: string;
  vues: number;
}

export interface PortRechercheVideos {
  rechercherVideos(ouverture: string): Promise<VideoExplicative[]>;
}
