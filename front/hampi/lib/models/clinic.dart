class Clinic {
  final String nombre;
  final String direccion;
  final Location ubicacion;

  Clinic({
    required this.nombre,
    required this.direccion,
    required this.ubicacion,
  });

  factory Clinic.fromJson(Map<String, dynamic> json) {
    return Clinic(
      nombre: json['nombre'] ?? '',
      direccion: json['direccion'] ?? '',
      ubicacion: Location.fromJson(json['ubicacion'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nombre': nombre,
      'direccion': direccion,
      'ubicacion': ubicacion.toJson(),
    };
  }
}

class Location {
  final double lat;
  final double lng;

  Location({
    required this.lat,
    required this.lng,
  });

  factory Location.fromJson(Map<String, dynamic> json) {
    return Location(
      lat: (json['lat'] ?? 0.0).toDouble(),
      lng: (json['lng'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'lat': lat,
      'lng': lng,
    };
  }
} 