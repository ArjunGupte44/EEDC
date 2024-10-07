#include <iostream>
#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#include <vector>

using namespace std;

struct CPUs {
   CPUs() : count(0), mod(1) {
      cpu_set_t cs;
      CPU_ZERO(&cs);
      sched_getaffinity(0, sizeof(cs), &cs);
      for (int i = 0; i < CPU_SETSIZE; ++i) {
         if (CPU_ISSET(i, &cs)) {
            ++count;
         }
      }
      mod = (count > 2) ? (count / 2) : 1;
   }

   int count, mod;
} cpus;

enum Color { blue = 0, red, yellow, Invalid };

ostream &operator<<(ostream &s, const Color &c) {
   static const char *names[] = { "blue", "red", "yellow", "Invalid" };
   s << names[c];
   return s;
}

Color operator+(const Color &c1, const Color &c2) {
   static const Color addition[3][3] = {
       {blue, yellow, red},
       {yellow, red, blue},
       {red, blue, yellow}
   };

   return addition[c1][c2];
}

string SpellNumber(int n) {
   static const char *numbers[] = {
       " zero", " one", " two",
       " three", " four", " five",
       " six", " seven", " eight",
       " nine"
   };

   string str;
   do {
      str.insert(0, numbers[n % 10]);
      n /= 10;
   } while (n);

   return str;
}

struct Creature;

struct MeetingPlace {
   enum { S = 4, creatureMask = (1 << S) - 1 };
   MeetingPlace(int N) : state(N << S) {
      creatures = new vector<Creature*>(N);
   }
   ~MeetingPlace() { delete[] creatures; }

   void Register(Creature &creature, int id);
   void MeetUp(Creature *creature);

protected:
   atomic<int> state;
   vector<Creature*> *creatures;
   int idGenerator = 0;
   mutex mtx;
};

struct Creature {
   Creature() : id(0), count(0), sameCount(0), met(false) {}

   int Display() const {
      cout << count << SpellNumber(sameCount) << endl;
      return count;
   }

   void Meet(Creature *other) {
      if (id == other->id) {
         sameCount++;
         other->sameCount++;
      }

      count++;
      other->count++;

      Color newcolor = color + other->color;
      other->color = color = newcolor;
      other->met = true;
   }

   void Init(MeetingPlace *mp, Color c, int id) {
      place = mp;
      initialColor = color = c;
      this->id = id;
      place->Register(*this, id);
   }

   void Run() {
      place->MeetUp(this);
   }

   void Start() {
      threadHandle = std::thread(&Creature::Run, this);
   }

   void Wait() {
      if (threadHandle.joinable())
         threadHandle.join();
   }

   int id, count, sameCount;
   bool met;
   Color initialColor, color;

protected:
   MeetingPlace *place;
   std::thread threadHandle;
};

void MeetingPlace::Register(Creature &creature, int id) {
   lock_guard<mutex> lock(mtx);
   creatures->at(id) = &creature;
}

void MeetingPlace::MeetUp(Creature *creature) {
   int useState = state;
   while (true) {
      int waiting = useState & creatureMask, tryState = 0;
      if (waiting)
         tryState = ((useState & ~creatureMask) - (1 << S));
      else if (useState)
         tryState = useState | creature->id;
      else
         return;

      int oldState = state.exchange(useState);
      if (oldState == useState) {
         if (waiting)
            creature->Meet(creatures->at(waiting));
         else
            while (!creature->met);
         useState = state;
      } else {
         useState = oldState;
      }
   }
}


int main(int argc, const char *argv[]) {
   const Color r1[] = {blue, red, yellow};
   const Color r2[] = {blue, red, yellow, red, yellow, blue, red, yellow, red, blue};

   for (int c1 = blue; c1 <= yellow; c1++)
      for (int c2 = blue; c2 <= yellow; c2++)
         cout << r1[c1] << " + " << r1[c2] << " -> " << (r1[c1] + r1[c2]) << endl;
   cout << endl;

   int n = (argc >= 2) ? atoi(argv[1]) : 6000000;

   vector<Creature> g1(3);
   vector<Creature> g2(10);

   MeetingPlace meetingPlace1(n), meetingPlace2(n);
   for (int i = 0; i < 3; i++)
      g1[i].Init(&meetingPlace1, r1[i], i);
   for (int i = 0; i < 10; i++)
      g2[i].Init(&meetingPlace2, r2[i], i);

   for (auto &creature : g1)
      creature.Start();
   for (auto &creature : g2)
      creature.Start();

   for (auto &creature : g1)
      creature.Wait();
   for (auto &creature : g2)
      creature.Wait();

   for (auto &creature : g1)
      creature.Display();
   for (auto &creature : g2)
      creature.Display();
}
