// DOM
const swiper = document.querySelector('#swiper');
const like = document.querySelector('#like');
const dislike = document.querySelector('#dislike');

// constants
const urls = [
  'https://i.pinimg.com/474x/7e/9f/95/7e9f950bd6bee173fdbe80742bfc4114.jpg',
'https://i.pinimg.com/474x/7e/9f/95/7e9f950bd6bee173fdbe80742bfc4114.jpg',
'https://i.pinimg.com/474x/7e/9f/95/7e9f950bd6bee173fdbe80742bfc4114.jpg',
'https://i.pinimg.com/474x/7e/9f/95/7e9f950bd6bee173fdbe80742bfc4114.jpg',
'https://i.pinimg.com/474x/7e/9f/95/7e9f950bd6bee173fdbe80742bfc4114.jpg'
];

// variables
let cardCount = 0;

// functions
function appendNewCard() {
  const card = new Card({
    imageUrl: urls[cardCount % 5],
    onDismiss: appendNewCard,
    onLike: () => {
      like.style.animationPlayState = 'running';
      like.classList.toggle('trigger');
    },
    onDislike: () => {
      dislike.style.animationPlayState = 'running';
      dislike.classList.toggle('trigger');
    }
  });
  swiper.append(card.element);
  cardCount++;

  const cards = swiper.querySelectorAll('.card:not(.dismissing)');
  cards.forEach((card, index) => {
    card.style.setProperty('--i', index);
  });
}

// first 5 cards
for (let i = 0; i < 5; i++) {
  appendNewCard();
}
