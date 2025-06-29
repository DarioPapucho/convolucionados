class AppConfig {
  static const String serverUrl = String.fromEnvironment(
    'SERVER_URL',
    defaultValue: 'http://192.168.23.222:8000',
  );
  
  static const String dentalEndpoint = '/dental/evaluate';
  static const String dermisEndpoint = '/dermis/evaluate';
  static const String coughEndpoint = '/cough/evaluate';
  
  static const String appName = 'Hampi';
  static const String appDescription = 'Evaluador de Lesiones';
  static const String appVersion = '1.0.0';
} 