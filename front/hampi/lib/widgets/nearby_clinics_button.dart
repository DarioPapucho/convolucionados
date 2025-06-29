import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../models/clinic.dart';
import '../services/api_service.dart';
import '../screens/clinics_map_screen.dart';

class NearbyClinicsButton extends StatefulWidget {
  const NearbyClinicsButton({super.key});

  @override
  State<NearbyClinicsButton> createState() => _NearbyClinicsButtonState();
}

class _NearbyClinicsButtonState extends State<NearbyClinicsButton> {
  bool _isLoading = false;

  Future<void> _showNearbyClinics() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Solicitar permisos de ubicación
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
        if (permission == LocationPermission.denied) {
          _showErrorSnackBar('Se requieren permisos de ubicación para mostrar clínicas cercanas');
          return;
        }
      }

      if (permission == LocationPermission.deniedForever) {
        _showErrorSnackBar('Los permisos de ubicación están permanentemente denegados');
        return;
      }

      // Obtener ubicación actual
      final Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      // Obtener clínicas cercanas
      final List<Clinic> clinics = await ApiService.getNearbyClinics(
        lat: position.latitude,
        lon: position.longitude,
        radio: 3000,
      );

      if (mounted) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => ClinicsMapScreen(
              clinics: clinics,
              userLat: position.latitude,
              userLng: position.longitude,
            ),
          ),
        );
      }
    } catch (e) {
      _showErrorSnackBar('Error al obtener clínicas cercanas: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : _showNearbyClinics,
        icon: _isLoading
            ? const SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.location_on, color: Colors.white),
        label: Text(
          _isLoading ? 'Buscando clínicas...' : 'Clínicas que te recomendamos para tu caso',
          style: const TextStyle(color: Colors.white),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Theme.of(context).colorScheme.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
        ),
      ),
    );
  }
} 