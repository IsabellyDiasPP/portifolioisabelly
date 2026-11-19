/* ===================================================================
   ROLO DE FOTOS DA CÂMERA — LOOP INFINITO (celular, tablet e desktop)
   Arquivo único: salve como rolo.js na mesma pasta do index.html.

   - A animação é feita em JS (requestAnimationFrame). Não depende do
     "-50%" do CSS, que falhava no celular quando a imagem da câmera
     ainda não tinha carregado (altura da janela = 0).
   - Mede a altura real de 1 ciclo (3 blocos) e, ao chegar no fim,
     volta exatamente 1 ciclo: não existe "fim" nem pulo.
   - Remonta sozinho quando a câmera carrega, a tela gira ou a barra
     do navegador muda a altura.
   - Pausa fora da tela, com a aba escondida e ao passar o mouse.
   =================================================================== */
(function () {
  'use strict';

  var track = document.getElementById('sliderTrack');
  if (!track) return;

  var janela = track.parentElement;                 // .trilha-fotos
  var hero = document.getElementById('home');
  var cameraImg = document.querySelector('.camera-img');

  // guarda 1 ciclo completo (os 3 blocos originais do HTML)
  var originais = Array.prototype.slice
    .call(track.querySelectorAll('.grid-fotos'), 0, 3)
    .map(function (b) { return b.cloneNode(true); });
  if (!originais.length) return;

  var VELOCIDADE = 0.22;  // larguras da janela por segundo (maior = mais rápido)
  var MAX_CICLOS = 40;    // trava de segurança

  var ciclo = 0;          // altura (px) de 1 ciclo
  var offset = 0;         // quanto já andou dentro do ciclo
  var ultimo = 0;
  var raf = 0;
  var rodando = false;
  var visivel = true;
  var pausadoMouse = false;
  var larguraMontada = -1;
  var alturaMontada = -1;
  var agendado = 0;

  var reduzirMovimento = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function clonar(bloco) {
    var c = bloco.cloneNode(true);
    c.setAttribute('aria-hidden', 'true');
    Array.prototype.forEach.call(c.querySelectorAll('img'), function (img) {
      img.setAttribute('alt', '');
      img.setAttribute('decoding', 'async');
      img.addEventListener('error', function () {   // foto faltando → reserva
        if (img.dataset.reserva) return;
        img.dataset.reserva = '1';
        img.src = 'IMG/feed1.jpg';
      });
    });
    return c;
  }

  function adicionarCiclo() {
    originais.forEach(function (b) { track.appendChild(clonar(b)); });
  }

  function aplicar() {
    track.style.transform = 'translate3d(0,' + (-offset).toFixed(2) + 'px,0)';
  }

  function montar() {
    larguraMontada = janela.clientWidth;
    alturaMontada = janela.clientHeight;
    // câmera ainda sem altura (celular)? usa a altura da tela como referência
    var alturaRef = alturaMontada || window.innerHeight;

    track.style.animation = 'none';                 // o JS assume o movimento
    track.style.transform = 'translate3d(0,0,0)';
    track.innerHTML = '';

    // 2 ciclos para medir 1 ciclo com precisão
    adicionarCiclo();
    adicionarCiclo();

    var n = originais.length;
    var medido =
      track.children[n].getBoundingClientRect().top -
      track.children[0].getBoundingClientRect().top;

    if (!(medido > 0)) { ciclo = 0; return; }       // layout ainda não existe; o observer chama de novo
    ciclo = medido;

    // repete ciclos até cobrir a janela + 1 ciclo de folga
    var ciclos = 2;
    while (
      track.getBoundingClientRect().height < alturaRef + ciclo * 1.05 &&
      ciclos < MAX_CICLOS
    ) {
      adicionarCiclo();
      ciclos++;
    }

    offset = offset % ciclo;                        // sem "pulo" ao remontar
    aplicar();
  }

  function quadro(agora) {
    if (!rodando) return;
    var dt = Math.min((agora - ultimo) / 1000, 0.05);
    ultimo = agora;

    if (ciclo > 0 && !pausadoMouse) {
      var largura = janela.clientWidth || 300;
      offset += VELOCIDADE * largura * dt;
      if (offset >= ciclo) offset -= ciclo;         // LOOP INFINITO
      aplicar();
    }
    raf = requestAnimationFrame(quadro);
  }

  function iniciar() {
    if (rodando || reduzirMovimento || !visivel || document.hidden) return;
    rodando = true;
    ultimo = performance.now();
    raf = requestAnimationFrame(quadro);
  }

  function parar() {
    rodando = false;
    cancelAnimationFrame(raf);
  }

  function refazer() {
    cancelAnimationFrame(agendado);
    agendado = requestAnimationFrame(function () {
      var w = janela.clientWidth;
      var h = janela.clientHeight;
      if (ciclo > 0 && Math.abs(w - larguraMontada) < 2 && Math.abs(h - alturaMontada) < 2) return;
      montar();
      iniciar();
    });
  }

  // ---------- liga tudo ----------
  montar();
  iniciar();

  if ('ResizeObserver' in window) new ResizeObserver(refazer).observe(janela);
  if (cameraImg) {
    if (!cameraImg.complete) cameraImg.addEventListener('load', refazer);
    cameraImg.addEventListener('error', refazer);
  }
  window.addEventListener('load', refazer);
  window.addEventListener('resize', refazer);
  window.addEventListener('orientationchange', function () { setTimeout(refazer, 300); });

  janela.addEventListener('mouseenter', function () { pausadoMouse = true; });
  janela.addEventListener('mouseleave', function () { pausadoMouse = false; });

  document.addEventListener('visibilitychange', function () {
    if (document.hidden) parar(); else iniciar();
  });

  if (hero && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (entradas) {
      visivel = entradas[0].isIntersecting;
      if (visivel) iniciar(); else parar();
    }).observe(hero);
  }
})();