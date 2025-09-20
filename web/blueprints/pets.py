"""
EXPLICACIÓN: Blueprint para gestión completa de mascotas.
Implementa CRUD con validaciones específicas y relación con propietarios.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date

from infra import get_container
from domain.entities.pet import PetSpecies, PetGender

# Crear blueprint
pets_bp = Blueprint('pets', __name__, template_folder='../templates/pets')

@pets_bp.route('/')
def list_pets():
    """
    RUTA: Lista de todas las mascotas
    """
    try:
        container = get_container()
        pet_service = container.get_pet_service()
        
        # Verificar si hay filtros
        search_query = request.args.get('search', '').strip()
        show_inactive = request.args.get('show_inactive', 'false') == 'true'
        
        if search_query:
            pets = pet_service.search_pets(search_query)
            flash(f'Encontradas {len(pets)} mascotas para "{search_query}"', 'info')
        else:
            pets = pet_service.get_all_pets(active_only=not show_inactive)
        
        return render_template(
            'pets/list.html', 
            pets=pets, 
            search_query=search_query,
            show_inactive=show_inactive
        )
        
    except Exception as e:
        print(f"Error listando mascotas: {e}")
        flash('Error cargando lista de mascotas.', 'error')
        return render_template('pets/list.html', pets=[], search_query='')

@pets_bp.route('/create', methods=['GET', 'POST'])
def create_pet():
    """
    RUTA: Crear nueva mascota
    """
    if request.method == 'GET':
        # Obtener cliente si viene como parámetro
        client_id = request.args.get('client_id')
        client = None
        
        if client_id:
            try:
                container = get_container()
                client_service = container.get_client_service()
                client = client_service.get_client_by_id(int(client_id))
            except:
                pass
        
        return render_template(
            'pets/create.html',
            species=PetSpecies,
            genders=PetGender,
            selected_client=client
        )
    
    try:
        # Obtener datos del formulario
        pet_data = {
            'name': request.form.get('name', '').strip(),
            'species': request.form.get('species', 'other'),
            'breed': request.form.get('breed', '').strip() or None,
            'birth_date': request.form.get('birth_date') or None,
            'gender': request.form.get('gender', 'unknown'),
            'color': request.form.get('color', '').strip() or None,
            'weight': request.form.get('weight') or None,
            'microchip_number': request.form.get('microchip_number', '').strip() or None,
            'client_id': int(request.form.get('client_id'))
        }
        
        # Convertir peso a float si existe
        if pet_data['weight']:
            try:
                pet_data['weight'] = float(pet_data['weight'])
            except ValueError:
                pet_data['weight'] = None
        
        # Crear mascota usando el service
        container = get_container()
        pet_service = container.get_pet_service()
        
        new_pet = pet_service.create_pet(pet_data)
        
        flash(f'Mascota {new_pet.name} registrada exitosamente.', 'success')
        return redirect(url_for('pets.view_pet', pet_id=new_pet.id))
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template(
            'pets/create.html',
            species=PetSpecies,
            genders=PetGender,
            **pet_data
        )
    
    except Exception as e:
        print(f"Error creando mascota: {e}")
        flash('Error registrando mascota.', 'error')
        return render_template(
            'pets/create.html',
            species=PetSpecies,
            genders=PetGender,
            **pet_data
        )

@pets_bp.route('/<int:pet_id>')
def view_pet(pet_id):
    """
    RUTA: Ver detalles de una mascota específica
    """
    try:
        container = get_container()
        pet_service = container.get_pet_service()
        appointment_service = container.get_appointment_service()
        
        # Obtener resumen completo de la mascota
        pet_summary = pet_service.get_pet_summary(pet_id)
        
        if not pet_summary:
            flash('Mascota no encontrada.', 'error')
            return redirect(url_for('pets.list_pets'))
        
        # Obtener historial de citas
        appointments = appointment_service.get_appointments_by_pet(pet_id)
        recent_appointments = sorted(appointments, key=lambda x: x.appointment_date, reverse=True)[:5]
        
        return render_template(
            'pets/view.html',
            pet_summary=pet_summary,
            recent_appointments=recent_appointments
        )
        
    except Exception as e:
        print(f"Error viendo mascota: {e}")
        flash('Error cargando información de la mascota.', 'error')
        return redirect(url_for('pets.list_pets'))

@pets_bp.route('/<int:pet_id>/edit', methods=['GET', 'POST'])
def edit_pet(pet_id):
    """
    RUTA: Editar mascota existente
    """
    try:
        container = get_container()
        pet_service = container.get_pet_service()
        
        # Obtener mascota existente
        pet = pet_service.get_pet_by_id(pet_id)
        if not pet:
            flash('Mascota no encontrada.', 'error')
            return redirect(url_for('pets.list_pets'))
        
    except Exception as e:
        flash('Error cargando mascota.', 'error')
        return redirect(url_for('pets.list_pets'))
    
    if request.method == 'GET':
        return render_template(
            'pets/edit.html',
            pet=pet,
            species=PetSpecies,
            genders=PetGender
        )
    
    try:
        # Obtener datos del formulario
        pet_data = {
            'name': request.form.get('name', '').strip(),
            'species': request.form.get('species'),
            'breed': request.form.get('breed', '').strip() or None,
            'birth_date': request.form.get('birth_date') or None,
            'gender': request.form.get('gender'),
            'color': request.form.get('color', '').strip() or None,
            'weight': request.form.get('weight') or None,
            'microchip_number': request.form.get('microchip_number', '').strip() or None,
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # Convertir peso a float si existe
        if pet_data['weight']:
            try:
                pet_data['weight'] = float(pet_data['weight'])
            except ValueError:
                pet_data['weight'] = None
        
        # Actualizar mascota usando el service
        updated_pet = pet_service.update_pet(pet_id, pet_data)
        
        flash(f'Mascota {updated_pet.name} actualizada exitosamente.', 'success')
        return redirect(url_for('pets.view_pet', pet_id=pet_id))
        
    except ValueError as e:
        flash(str(e), 'error')
        return render_template(
            'pets/edit.html',
            pet=pet,
            species=PetSpecies,
            genders=PetGender
        )
    
    except Exception as e:
        print(f"Error actualizando mascota: {e}")
        flash('Error actualizando mascota.', 'error')
        return render_template(
            'pets/edit.html',
            pet=pet,
            species=PetSpecies,
            genders=PetGender
        )

@pets_bp.route('/<int:pet_id>/deactivate', methods=['POST'])
def deactivate_pet(pet_id):
    """
    RUTA: Desactivar mascota (soft delete)
    """
    try:
        container = get_container()
        pet_service = container.get_pet_service()
        
        pet = pet_service.get_pet_by_id(pet_id)
        if not pet:
            flash('Mascota no encontrada.', 'error')
            return redirect(url_for('pets.list_pets'))
        
        # Desactivar mascota
        success = pet_service.deactivate_pet(pet_id)
        
        if success:
            flash(f'Mascota {pet.name} desactivada exitosamente.', 'success')
        else:
            flash('Error desactivando mascota.', 'error')
        
        return redirect(url_for('pets.view_pet', pet_id=pet_id))
        
    except Exception as e:
        print(f"Error desactivando mascota: {e}")
        flash('Error desactivando mascota.', 'error')
        return redirect(url_for('pets.list_pets'))

@pets_bp.route('/by-client/<int:client_id>')
def pets_by_client(client_id):
    """
    RUTA: Mascotas de un cliente específico
    """
    try:
        container = get_container()
        pet_service = container.get_pet_service()
        client_service = container.get_client_service()
        
        # Verificar que el cliente existe
        client = client_service.get_client_by_id(client_id)
        if not client:
            flash('Cliente no encontrado.', 'error')
            return redirect(url_for('clients.list_clients'))
        
        # Obtener mascotas del cliente
        pets = pet_service.get_pets_by_client(client_id)
        
        return render_template(
            'pets/by_client.html',
            pets=pets,
            client=client
        )
        
    except Exception as e:
        print(f"Error obteniendo mascotas del cliente: {e}")
        flash('Error cargando mascotas del cliente.', 'error')
        return redirect(url_for('clients.list_clients'))

@pets_bp.route('/search')
def search_pets():
    """
    RUTA: Búsqueda AJAX de mascotas
    """
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify([])
        
        container = get_container()
        pet_service = container.get_pet_service()
        
        pets = pet_service.search_pets(query)
        
        # Formatear para JSON
        results = []
        for pet in pets[:10]:  # Máximo 10 resultados
            # Obtener info del propietario
            try:
                client_service = container.get_client_service()
                owner = client_service.get_client_by_id(pet.client_id)
                owner_name = owner.full_name if owner else "Propietario desconocido"
            except:
                owner_name = "Propietario desconocido"
            
            results.append({
                'id': pet.id,
                'name': pet.name,
                'species': pet.species.value.title(),
                'owner': owner_name,
                'display': f"{pet.name} ({pet.species.value.title()}) - {owner_name}"
            })
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error en búsqueda de mascotas: {e}")
        return jsonify([])