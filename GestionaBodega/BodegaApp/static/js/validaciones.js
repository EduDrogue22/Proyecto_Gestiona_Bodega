function error(message){
    Swal.fire({
        titleText: "Error",
        text: message,
        icon: "error",
        confirmButtonText: "Ok"
    })
}

function exito(message){
    Swal.fire({
        titleText: "success",
        text: message,
        icon: "success",
        confirmButtonText: "Ok"
    })
}

function validarPerfil(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var nombrePerfil = document.getElementById("nombre_perfil").value;

    if (nombrePerfil == "" || nombrePerfil == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (nombrePerfil.length < 3) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de perfil muy corto',
        });
        validacionCorrecta = false;
    } else if (nombrePerfil.length > 50) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de perfil muy largo',
        });
        validacionCorrecta = false;
    } else if (nombrePerfil.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre de perfil tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            text: 'Perfil de usuario agregado exitosamente',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function() {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 3000); // 2000 milisegundos = 2 segundos
    }
}

var validacionCorrecta = true;
function validarUsuarioCliente(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var primer_nombre = document.getElementById("txtPrimerNombre").value;
    var apellido_paterno = document.getElementById("txtApellidoPaterno").value;
    var apellido_materno = document.getElementById("txtApellidoMaterno").value;
    var rut = document.getElementById("numRut").value;
    var correo = document.getElementById("txtCorreo").value;
    var contrasena = document.getElementById("txtContrasena").value;
    var rept_contrasena = document.getElementById("txtReptContrasena").value;

    if (primer_nombre == "" || primer_nombre == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'El primer nombre no debe estar en blanco',
        });
        validacionCorrecta = false;
    } else if (apellido_paterno == "" || apellido_materno == null) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El apellido paterno no debe estar en blanco.',
        });
        validacionCorrecta = false;
    } else if (apellido_materno == "" || apellido_materno == null) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El apellido materno no debe estar en blanco.',
        });
        validacionCorrecta = false;
    } else if (primer_nombre.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El primer nombre tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (apellido_paterno.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El apellido paterno tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (apellido_materno.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El apellido materno tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (rut == "" || rut == null) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El rut no debe estar en blanco.',
        });
        validacionCorrecta = false;
    } else if (rut.length > 11) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El rut es demasiado largo.',
        });
        validacionCorrecta = false;
    } else if (rut.length < 8) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El rut es corto.',
        });
        validacionCorrecta = false;
    } else if (rut.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El rut tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (correo == "" || correo == null) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El correo no debe estar en blanco.',
        });
        validacionCorrecta = false;
    } else if (correo.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El correo tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (contrasena != rept_contrasena) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'La contraseña no es similar.',
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            text: 'Perfil de usuario agregado exitosamente',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function() {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 3000); // 2000 milisegundos = 2 segundos
    }
}