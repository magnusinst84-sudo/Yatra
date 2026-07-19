import patliputraImg from './images_re/patliputa.jpeg';
import elloraImg from './images_re/ellora.jpeg';
import thanjavurImg from './images_re/thanjavur.jpeg';
import maduraiImg from './images_re/madhurai.jpeg';
import goldenTempleImg from './images_re/golden_temple.jpeg';

export interface Destination {
  id: string;
  name: string;
  era: string;
  location: string;
  description: string;
  image: string; // Dynamic bundled image asset URL
  gradient: string; // Background cinematic gradient
  cardGradient: string; // Card specific gradient
  accentColor: string; // Accents for UI details
}

export const destinations: Destination[] = [
  {
    id: "taj-mahal",
    name: "Patliputra",
    era: "Maurya Empire",
    location: "Patna, Bihar",
    description: "The legendary capital city of ancient India, ruling over the Maurya and Gupta Empires. Once one of the largest cities in the world, Patliputra was a major center of learning, philosophy, trade, and the capital of legendary emperors Chandragupta Maurya and Ashoka the Great.",
    image: patliputraImg,
    gradient: "linear-gradient(to bottom, rgba(7, 7, 10, 0.7), rgba(7, 7, 10, 0.95)), linear-gradient(135deg, #1e1b29 0%, #0d0d12 100%)",
    cardGradient: "linear-gradient(135deg, rgba(74, 52, 108, 0.3) 0%, rgba(13, 13, 18, 0.9) 100%)",
    accentColor: "#AA7C11"
  },
  {
    id: "hampi",
    name: "Ellora",
    era: "Rashtrakuta Dynasty",
    location: "Aurangabad, Maharashtra",
    description: "A monumental rock-cut cave complex hosting 34 Hindu, Buddhist, and Jain temples carved out of the Charanandri hills. It features the breathtaking Kailasha temple (Cave 16), the largest monolithic rock-cut structure in the world, carved from the top down with remarkable precision.",
    image: elloraImg,
    gradient: "linear-gradient(to bottom, rgba(7, 7, 10, 0.7), rgba(7, 7, 10, 0.95)), linear-gradient(135deg, #2b1f14 0%, #0d0d12 100%)",
    cardGradient: "linear-gradient(135deg, rgba(120, 75, 30, 0.25) 0%, rgba(13, 13, 18, 0.9) 100%)",
    accentColor: "#D4AF37"
  },
  {
    id: "varanasi",
    name: "Thanjavur",
    era: "Chola Empire",
    location: "Thanjavur, Tamil Nadu",
    description: "The imperial capital of the Chola Dynasty, housing the magnificent Brihadeeswarar Temple. Completed in 1010 AD by Rajaraja Chola I, its massive granite tower and giant monolithic Nandi bull sculpture stand as crowning triumphs of Dravidian temple architecture.",
    image: thanjavurImg,
    gradient: "linear-gradient(to bottom, rgba(7, 7, 10, 0.7), rgba(7, 7, 10, 0.95)), linear-gradient(135deg, #1c2e36 0%, #0d0d12 100%)",
    cardGradient: "linear-gradient(135deg, rgba(30, 80, 95, 0.2) 0%, rgba(13, 13, 18, 0.9) 100%)",
    accentColor: "#E5A93C"
  },
  {
    id: "khajuraho",
    name: "Madurai Temples",
    era: "Pandya Kingdom",
    location: "Madurai, Tamil Nadu",
    description: "The historical heart of Tamil Nadu, famous for the sprawling Meenakshi Amman Temple complex. Adorned with twelve towering gopurams decorated in a vibrant tapestry of multi-colored stucco figures representing deities, legendary warriors, and ancient Indian myths.",
    image: maduraiImg,
    gradient: "linear-gradient(to bottom, rgba(7, 7, 10, 0.7), rgba(7, 7, 10, 0.95)), linear-gradient(135deg, #2d1c1c 0%, #0d0d12 100%)",
    cardGradient: "linear-gradient(135deg, rgba(110, 40, 40, 0.2) 0%, rgba(13, 13, 18, 0.9) 100%)",
    accentColor: "#C98E3A"
  },
  {
    id: "ajanta",
    name: "Golden Temple",
    era: "Sikh Empire",
    location: "Amritsar, Punjab",
    description: "The preeminent spiritual sanctuary of Sikhism. Built around a beautiful sarovar (sacred pool) and completed by Guru Arjan Dev, this gold-gilded temple represents eternal peace, spiritual freedom, and equal treatment of all people, welcoming visitors from all walks of life.",
    image: goldenTempleImg,
    gradient: "linear-gradient(to bottom, rgba(7, 7, 10, 0.7), rgba(7, 7, 10, 0.95)), linear-gradient(135deg, #12211b 0%, #0d0d12 100%)",
    cardGradient: "linear-gradient(135deg, rgba(20, 80, 50, 0.2) 0%, rgba(13, 13, 18, 0.9) 100%)",
    accentColor: "#D4AF37"
  }
];
