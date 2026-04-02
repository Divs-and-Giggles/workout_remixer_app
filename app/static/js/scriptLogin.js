document.addEventListener('DOMContentLoaded', () => {
        const container = document.getElementById('container');
        const loginButton = document.getElementById('login');
        const registerButton = document.getElementById('register');
        const wrapper = document.querySelector('.toggle');
        const bg = document.querySelector('body');

        if(registerButton) {
            registerButton.addEventListener('click', () => {
                container.classList.add('active');
                wrapper.classList.add('active');
                bg.classList.add('active');
            });
        }

        if(loginButton) {
            loginButton.addEventListener('click', () => {
                container.classList.remove('active');
                wrapper.classList.remove('active');
                bg.classList.remove('active');
            });
        }
    });