import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import '../models/clinic.dart';
import '../services/api_service.dart';

class ClinicsMapScreen extends StatefulWidget {
  final List<Clinic> clinics;
  final double userLat;
  final double userLng;

  const ClinicsMapScreen({
    super.key,
    required this.clinics,
    required this.userLat,
    required this.userLng,
  });

  @override
  State<ClinicsMapScreen> createState() => _ClinicsMapScreenState();
}

class _ClinicsMapScreenState extends State<ClinicsMapScreen> {
  GoogleMapController? _mapController;
  Set<Marker> _markers = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _initializeMap();
  }

  void _initializeMap() {
    _createMarkers();
    setState(() {
      _isLoading = false;
    });
  }

  void _createMarkers() {
    final markers = <Marker>{};

    // Marcador del usuario
    markers.add(
      Marker(
        markerId: const MarkerId('user'),
        position: LatLng(widget.userLat, widget.userLng),
        infoWindow: const InfoWindow(
          title: 'Tu ubicación',
          snippet: 'Ubicación actual',
        ),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueBlue),
      ),
    );

    // Marcadores de las clínicas
    for (int i = 0; i < widget.clinics.length; i++) {
      final clinic = widget.clinics[i];
      markers.add(
        Marker(
          markerId: MarkerId('clinic_$i'),
          position: LatLng(clinic.ubicacion.lat, clinic.ubicacion.lng),
          infoWindow: InfoWindow(
            title: clinic.nombre,
            snippet: clinic.direccion,
          ),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueRed),
        ),
      );
    }

    setState(() {
      _markers = markers;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Clínicas Cercanas'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Expanded(
                  child: GoogleMap(
                    onMapCreated: (GoogleMapController controller) {
                      _mapController = controller;
                    },
                    initialCameraPosition: CameraPosition(
                      target: LatLng(widget.userLat, widget.userLng),
                      zoom: 14.0,
                    ),
                    markers: _markers,
                    myLocationEnabled: true,
                    myLocationButtonEnabled: true,
                    zoomControlsEnabled: true,
                    mapToolbarEnabled: true,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 4,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Clínicas encontradas: ${widget.clinics.length}',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Punto azul: Tu ubicación\nPuntos rojos: Clínicas cercanas',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }

  @override
  void dispose() {
    _mapController?.dispose();
    super.dispose();
  }
} 