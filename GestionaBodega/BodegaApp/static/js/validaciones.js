// Expresión regular mejorada para validar correos electrónicos,rut y nombres de usuario
var formatoCorreo = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
var formatoRut = /^(\d{7,8}-[0-9Kk])$/;
var formatoNombre = /^[A-Za-zñÑ\s]+$/;

// Declarar la variable validacionCorrecta
var validacionCorrecta = true;

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

function exitoLogin(message, id_usuario) {
    Swal.fire({
        titleText: "Iniciando Sesion",
        text: message,
        icon: "success",
        showConfirmButton: false,
        timer: 2500
    }).then(() => {
        if (id_usuario == 1) {
            window.location.href = '/inicio';
        }
        else if (id_usuario == 2) {
            window.location.href = '/home_colab';
        }
        else{
            window.location.href = '/menuAdmin';
        }
    });
}


function errorProd(message){
    Swal.fire({
        icon: 'error',
        title: 'Error',
        text: message,
        confirmButtonText: 'Volver'
      })
}

function exitoProd(message, title){
  Swal.fire({
      icon: 'success',
      title: title,
      text: message,
      showConfirmButton: false,
      timer: 2000
    }).then(() => {
        window.location.href = '/producto';
      });
}

function eliminarProd(nombre_prod, id) {
    Swal.fire({
        title: 'Desea eliminar el producto ' + nombre_prod + '?',
        showCancelButton: true,
        confirmButtonText: 'Eliminar',
    }).then((result) => {
        if (result.isConfirmed) {
            // Hacer la solicitud para eliminar el producto
            fetch('/eliminar_producto/' + id + '/')
                .then(response => response.json())
                .then((response) => {
                    if (response['status'] === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Producto Eliminado',
                            text: response['exito_message'],
                            showConfirmButton: false,
                            timer: 2000
                        }).then(() => {
                            // Redirigir después de mostrar el mensaje de éxito
                            window.location.href = '/producto';
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: response['error_message'],
                            showConfirmButton: true,
                        });
                    }
                });
        }
    });
}

// En algún lugar donde procesas la respuesta del servidor

function exitoDespacho(idProducto) {
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    Swal.fire({
        title: 'Ingrese cantidad de producto a despachar',
        input: 'text',
        showCancelButton: true,
        confirmButtonText: `<i class="fa fa-thumbs-up"></i> Aceptar`,
    }).then((result) => {
        if (result.isConfirmed) {
            let cantidadDespachar = result.value;
            let rutcli = document.getElementById("rut_cli_" + idProducto).value;

            console.log("Valor de id_producto antes de la solicitud AJAX:", idProducto);


            $.ajax({
                url: '/despachar/',  // Reemplaza con la ruta correcta
                type: 'POST',
                data: {
                    cantidad_despachar: cantidadDespachar,
                    id_producto: idProducto,
                    rut: rutcli,
                    csrfmiddlewaretoken: csrftoken,  // Necesario para la protección CSRF
                },
                
                success: function(response) {
                    if (response.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Producto Despachado',
                            text: response.exito_message,
                            showConfirmButton: false,
                            timer: 2000
                          }).then(() => {
                              window.location.href = '/despacho';
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: response.error_message,
                        });
                    }
                },
                error: function(error) {
                    console.error(error);
                    if (error.responseJSON) {
                        console.log("Respuesta del servidor:", error.responseJSON);
                    }
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Hubo un problema al despachar el producto.',
                    });
                }
            });
        }
    });
}

// Validar agregar perfil de usuario Admin
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
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }
}

// Validar agregar plan Admin
function validarPlan(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var nombrePlan = document.getElementById("nombre_plan").value;
    var costoPlan = document.getElementById("costo").value;
    var cantAnaquelesPlan = document.getElementById("cant_anaqueles").value;
    var capacidadPlan = document.getElementById("capacidad").value;

    if (nombrePlan == "" || nombrePlan == null || costoPlan == "" || costoPlan == null ||
        cantAnaquelesPlan == "" || cantAnaquelesPlan == null || capacidadPlan == "" || capacidadPlan == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (nombrePlan.length < 3) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de plan muy corto',
        });
        validacionCorrecta = false;
    } else if (nombrePlan.length > 30) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de plan muy largo',
        });
        validacionCorrecta = false;
    } else if (nombrePlan.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre del plan tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (costoPlan < 0 || costoPlan > 9999999999) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El costo del plan ingresado no valido'
        });
        validacionCorrecta = false;
    } else if (cantAnaquelesPlan < 0 || cantAnaquelesPlan > 9999) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'La cantidad de anaqueles ingresados no validos'
        });
        validacionCorrecta = false;
    } else if (capacidadPlan < 0 || capacidadPlan > 999) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'La capacidad ingresada no valida'
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 3 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }
}

// Validar agregar Empresa Admin
function validarEmpresas(event) {

    event.preventDefault(); // Evitar el envío automático del formulario

    var nombreEmpresa = document.getElementById("nombre_empresa").value;
    var rutEmpresa = document.getElementById("rut_emp").value;
    var desEmpresa = document.getElementById("descrip_emp").value;

    if (nombreEmpresa == "" || nombreEmpresa == null || rutEmpresa == "" || rutEmpresa == null
        || desEmpresa == "" || desEmpresa == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (nombreEmpresa.length < 1) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de empresa muy corto',
        });
        validacionCorrecta = false;
    } else if (nombreEmpresa.length > 50) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de empresa muy largo',
        });
        validacionCorrecta = false;
    } else if (nombreEmpresa.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre de la empresa tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (!formatoRut.test(rutEmpresa)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'RUT ingresado no válido'
        });
        validacionCorrecta = false;
    } else if (desEmpresa.length < 5) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Descripción de empresa muy corto',
        });
        validacionCorrecta = false;
    } else if (desEmpresa.length > 100) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Descripción de empresa muy largo',
        });
        validacionCorrecta = false;
    } else if (desEmpresa.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'La descripción de la empresa tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 3 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }
}

// Validar agregar prodcuto admin
function validarProducto(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var nombreProducto = document.getElementById("nombre_pro").value;
    var stockProducto = document.getElementById("stock").value;

    if (nombreProducto == "" || nombreProducto == null || stockProducto == "" || stockProducto == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (nombreProducto.length < 2) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de producto muy corto',
        });
        validacionCorrecta = false;
    } else if (nombreProducto.length > 50) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de producto muy largo',
        });
        validacionCorrecta = false;
    } else if (nombreProducto.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre del producto tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (stockProducto < 0 || stockProducto > 999999999) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El stock ingresado no es valido'
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 3 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }
}

// Validar agregar sucursal admin
function validarSucursal(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var nombreSucursal = document.getElementById("nombre_sus").value;
    var direccionSucursal = document.getElementById("direccion_sus").value;

    if (nombreSucursal == "" || nombreSucursal == null || direccionSucursal == "" || direccionSucursal == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (nombreSucursal.length < 3) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de sucursal muy corto',
        });
        validacionCorrecta = false;
    } else if (nombreSucursal.length > 50) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de sucursal muy largo',
        });
        validacionCorrecta = false;
    } else if (nombreSucursal.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre de la sucursal tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (direccionSucursal.length < 5) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección muy corta',
        });
        validacionCorrecta = false;
    } else if (direccionSucursal.length > 100) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección muy largo',
        });
        validacionCorrecta = false;
    } else if (direccionSucursal.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }

}

// Validar agregar bodega admin
function validarBodega(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var nombreBodega = document.getElementById("nombre_bod").value;
    var direccionBodega = document.getElementById("direccion_bod").value;

    if (nombreBodega == "" || nombreBodega == null || direccionBodega == "" || direccionBodega == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (nombreBodega.length < 3) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de bodega muy corto',
        });
        validacionCorrecta = false;
    } else if (nombreBodega.length > 70) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de sucursal muy largo',
        });
        validacionCorrecta = false;
    } else if (nombreBodega.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre de la bodega tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (direccionBodega.length < 5) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección muy corta',
        });
        validacionCorrecta = false;
    } else if (direccionBodega.length > 70) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección muy largo',
        });
        validacionCorrecta = false;
    } else if (direccionBodega.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 3 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }

}

// Validar agregar área bodega admin
function validarAreaBodega(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var sectorBodega = document.getElementById("sector_area").value;
    var anaquelesBodega = document.getElementById("anaqueles_area").value;

    if (sectorBodega == "" || sectorBodega == null || anaquelesBodega == "" || anaquelesBodega == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (sectorBodega.length > 4) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Nombre de sector muy largo',
        });
        validacionCorrecta = false;
    } else if (sectorBodega.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'El nombre del sector tiene solamente espacios en blanco',
        });
        validacionCorrecta = false;
    } else if (anaquelesBodega < 0 || anaquelesBodega > 999) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'La cantidad de anaqueles no es valida'
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }

}

// Calcular la fecha mínima (1 de enero de 1900) y la edad mínima (18 años)
var fechaMinima = new Date('1900-01-01');
var edadMinima = 18;

// Obtener la fecha actual
var fechaActual = new Date();

function validarCliente(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var primerNombe = document.getElementById("p_nombre_cli").value;
    var segundoNombre = document.getElementById("s_nombre_cli").value;
    var apellidoPaterno = document.getElementById("ap_apellido_cli").value;
    var apellidoMaterno = document.getElementById("am_apellido_cli").value;
    var rutCliente = document.getElementById("rut_cli").value;
    var correoCliente = document.getElementById("mail_cli").value;
    var fechaNacimiento = document.getElementById("fecha_nac").value;
    var direccion = document.getElementById("direccion_cli").value;
    var passc1 = document.getElementById("pass_cli").value;
    var passc2 = document.getElementById("pass_cli_re").value;

    // Obtener la fecha actual
    var fechaNac = new Date(fechaNacimiento);

    // Calcular la edad del usuario
    var edadUsuario = fechaActual.getFullYear() - fechaNac.getFullYear();

    if (primerNombe == "" || primerNombe == null || segundoNombre == "" || segundoNombre == null
        || apellidoPaterno == "" || apellidoPaterno == null || apellidoMaterno == "" || apellidoMaterno == null
        || correoCliente == "" || correoCliente == null || fechaNacimiento == "" || fechaNacimiento == null
        || direccion == "" || direccion == null || passc1 == "" || passc1 == null || passc2 == "" || passc2 == null
        || rutCliente == "" || rutCliente == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (primerNombe.length < 1 || primerNombe.length > 50 || primerNombe.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Primer nombre no valido',
        });
        validacionCorrecta = false;
    } else if (segundoNombre.length < 1 || segundoNombre.length > 50 || segundoNombre.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Segundo nombre no valido',
        });
        validacionCorrecta = false;
    } else if (apellidoPaterno.length < 1 || apellidoPaterno.length > 50 || apellidoPaterno.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido paterno no valido',
        });
        validacionCorrecta = false;
    } else if (apellidoMaterno.length < 1 || apellidoMaterno.length > 50 || apellidoMaterno.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido paterno no valido',
        });
        validacionCorrecta = false;
    } else if (!formatoRut.test(rutCliente)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'RUT ingresado no válido'
        });
        validacionCorrecta = false;
    } else if (!formatoCorreo.test(correoCliente)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Correo ingresado no válido'
        });
        validacionCorrecta = false;
    } else if (fechaNac < fechaMinima || edadUsuario < edadMinima) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Fecha de nacimiento no válido'
        });
        validacionCorrecta = false;
    } else if (direccion.length < 3 || direccion.length > 100 || direccion.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Dirección no valida',
        });
        validacionCorrecta = false;
    } else if (passc1.length < 8 || passc2.length < 8) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Contraseña muy corta',
        })
        return false;
    } else if (passc1 != passc2) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Las contraseñas deben ser iguales',

        })
        return false;
    } else if (!formatoNombre.test(primerNombe)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Primer nombre ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else if (!formatoNombre.test(segundoNombre)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Segundo nombre ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else if (!formatoNombre.test(apellidoMaterno)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido materno ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else if (!formatoNombre.test(apellidoPaterno)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido paterno ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }
}

function validarEmpleado(event) {
    event.preventDefault();

    var primerNombe = document.getElementById("p_nombre_emp").value;
    var segundoNombre = document.getElementById("s_nombre_emp").value;
    var apellidoPaterno = document.getElementById("ap_apellido_emp").value;
    var apellidoMaterno = document.getElementById("am_apellido_emp").value;
    var rutEmp = document.getElementById("rut_emp").value;
    var correoEmp = document.getElementById("mail_emp").value;
    var pass1 = document.getElementById("pass_emp").value;
    var pass2 = document.getElementById("pass_emp_re").value;

    if (primerNombe == "" || primerNombe == null || segundoNombre == "" || segundoNombre == null
        || apellidoPaterno == "" || apellidoPaterno == null || apellidoMaterno == "" || apellidoMaterno == null
        || correoEmp == "" || correoEmp == null || pass1 == "" || pass1 == null || pass2 == "" || pass2 == null
        || rutEmp == "" || rutEmp == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (primerNombe.length < 1 || primerNombe.length > 50 || primerNombe.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Primer nombre no valido',
        });
        validacionCorrecta = false;
    } else if (segundoNombre.length < 1 || segundoNombre.length > 50 || segundoNombre.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Segundo nombre no valido',
        });
        validacionCorrecta = false;
    } else if (apellidoPaterno.length < 1 || apellidoPaterno.length > 50 || apellidoPaterno.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido paterno no valido',
        });
        validacionCorrecta = false;
    } else if (apellidoMaterno.length < 1 || apellidoMaterno.length > 50 || apellidoMaterno.trim().length == 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido paterno no valido',
        });
        validacionCorrecta = false;
    } else if (!formatoRut.test(rutEmp)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'RUT ingresado no válido'
        });
        validacionCorrecta = false;
    } else if (!formatoCorreo.test(correoEmp)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Correo ingresado no válido'
        });
        validacionCorrecta = false;
    } else if (pass1.length < 8 || pass2.length < 8) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Contraseña muy corta',
        })
        return false;
    } else if (pass1 != pass2) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Las contraseñas deben ser iguales',

        })
        return false;
    } else if (!formatoNombre.test(primerNombe)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Primer nombre ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else if (!formatoNombre.test(segundoNombre)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Segundo nombre ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else if (!formatoNombre.test(apellidoMaterno)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido materno ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else if (!formatoNombre.test(apellidoPaterno)) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Apellido paterno ingresado no válido, tiene números'
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }

}

// Validar agregar perfil de usuario Admin
function validarDespacho(event) {
    event.preventDefault(); // Evitar el envío automático del formulario

    var Tentrega = document.getElementById("TEntrega").value;

    if (Tentrega == "" || Tentrega == null) {
        Swal.fire({
            icon: 'warning',
            title: 'Advertencia',
            text: 'Todos los campos son obligatorios',
        });
        validacionCorrecta = false;
    } else if (Tentrega < 0) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Tiempo de Entrega tiene números negativos',
        });
        validacionCorrecta = false;
    } else if (Tentrega > 999) {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Tiempo de Entrega es demasiado largo',
        });
        validacionCorrecta = false;
    } else {
        // Los datos son válidos, mostrar SweetAlert de éxito
        Swal.fire({
            icon: 'success',
            title: 'Éxito',
            showConfirmButton: false,
            text: '',
        });

        // Agregar un retraso de 2 segundos antes de enviar el formulario
        setTimeout(function () {
            event.target.submit(); // Envía el formulario manualmente después del retraso
        }, 2000);
    }
}