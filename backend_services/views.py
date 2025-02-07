from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import exifread
import hashlib
import io

class ImageProcessingView(APIView):
    def post(self, request):
        print("hii")
        image_url = request.data.get('image_url')
        if not image_url:
            return Response({'error': 'image_url is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Download the image
        try:
            response = requests.get(image_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Failed to download image: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        image_content = response.content
        
        # Generate image hash (first 16 chars of SHA-256 hex digest)
        image_hash = hashlib.sha256(image_content).hexdigest()[:16]
        
        # Process EXIF data
        try:
            tags = exifread.process_file(io.BytesIO(image_content), details=False)
        except Exception as e:
            return Response({
            'image_hash': image_hash, 
        })
        
        # Extract EXIF DateTimeOriginal
        datetime_tag = tags.get('EXIF DateTimeOriginal')
        if not datetime_tag:
            return Response({
            'image_hash': image_hash
        },status=status.HTTP_200_OK)
        
        try:
            datetime_str = str(datetime_tag)
            if ' ' not in datetime_str:
                raise ValueError('Invalid DateTimeOriginal format')
            date_part, time_part = datetime_str.split(' ', 1)
            formatted_date = date_part.replace(':', '-', 2)
            exif_timestamp = f"{formatted_date}T{time_part}Z"
        except Exception as e:
            return Response({
            'image_hash': image_hash
        },status=status.HTTP_200_OK)
        
        
        # Extract GPS coordinates
        gps_latitude = tags.get('GPS GPSLatitude')
        gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
        gps_longitude = tags.get('GPS GPSLongitude')
        gps_longitude_ref = tags.get('GPS GPSLongitudeRef')
        
        if not all([gps_latitude, gps_latitude_ref, gps_longitude, gps_longitude_ref]):
            return Response({
            'image_hash': image_hash
        },status=status.HTTP_200_OK)
        
        
        try:
            lat = self._convert_gps_to_decimal(gps_latitude, gps_latitude_ref)
            lon = self._convert_gps_to_decimal(gps_longitude, gps_longitude_ref)
        except Exception as e:
            return Response({
            'image_hash': image_hash
        },status=status.HTTP_200_OK)
        
        
        exif_gps = f"{lat:.4f},{lon:.4f}"
        
        return Response({
            'image_hash': image_hash,
            'exif_timestamp': exif_timestamp,
            'exif_gps_location': exif_gps
        },status=status.HTTP_200_OK)
    
    def _convert_gps_to_decimal(self, coord, ref):
        # Convert each part from Rational to float
        degrees = coord.values[0].num / coord.values[0].den
        minutes = coord.values[1].num / coord.values[1].den
        seconds = coord.values[2].num / coord.values[2].den
        
        decimal = degrees + (minutes / 60) + (seconds / 3600)
        
        # Adjust sign based on direction (N/S, E/W)
        ref_str = str(ref.values).strip().upper()
        if ref_str in ['S', 'W']:
            decimal = -decimal
        
        return decimal