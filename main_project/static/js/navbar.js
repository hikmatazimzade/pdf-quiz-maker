var mainNav = document.getElementById('mainNav')
      var logoImg = document.getElementById('logoImg')
      var hero = document.getElementById('hero')
      var heroActive = false
      window.addEventListener('scroll', function() {
        if (window.scrollY > 200) {
          if (!heroActive) {
            heroActive = true
            mainNav.classList.add('bg-dark')
            if(window.innerWidth < 956) return;
            logoImg.className = 'consize'
          }
        } else {
          if (heroActive) {
            heroActive = false
            mainNav.classList.remove('bg-dark')
            if(window.innerWidth < 956) return;
            logoImg.className = ''
          }
        }
      })