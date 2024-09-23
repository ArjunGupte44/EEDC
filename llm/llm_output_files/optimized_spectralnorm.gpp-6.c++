#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <sched.h>
#include <omp.h>
#include <emmintrin.h>

// Optimized Index Function
int IndexOptimized(int i_plus_j, int i, int j, bool modei) {
    return (((i_plus_j) * (i_plus_j + 1)) >> 1) + (modei ? i : j) + 1;
}

void EvalPartOptimized(double *__restrict__ src, double *__restrict__ dst,
                       int begin, int end, int length, bool modei) {
    int i = begin;
    for (; i + 1 < end; i += 2) {
        __m128d sum = _mm_set_pd(
            src[0] / double(IndexOptimized(i + 1, i + 1, 0, modei)),
            src[0] / double(IndexOptimized(i + 0, i + 0, 0, modei)));

        __m128d ti = _mm_set_pd(i + 1, i + 0);
        if (!modei) ti = ti + _mm_set1_pd(1.0);

        __m128d last = _mm_set_pd(IndexOptimized(i + 1, i + 1, 0, modei),
                                  IndexOptimized(i + 0, i + 0, 0, modei));

        for (int j = 1; j < length; j++) {
            __m128d idx = last + ti + _mm_set1_pd(j);
            last = idx;
            sum = sum + _mm_set1_pd(src[j]) / idx;
        }

        _mm_storeu_pd(dst + i + 0, sum);
    }
    for (; i < end; i++) {
        double sum = 0;
        for (int j = 0; j < length; j++)
            sum += src[j] / double(IndexOptimized(i + j, i, j, modei));
        dst[i] = sum;
    }
}

void EvalATimesU(double *src, double *dst, int begin, int end, int N) {
    EvalPartOptimized(src, dst, begin, end, N, true);
}

void EvalAtTimesU(double *src, double *dst, int begin, int end, int N) {
    EvalPartOptimized(src, dst, begin, end, N, false);
}

void EvalAtATimesU(double *src, double *dst, double *tmp,
                   int begin, int end, int N) {
    EvalATimesU(src, tmp, begin, end, N);
    #pragma omp barrier
    EvalAtTimesU(tmp, dst, begin, end, N);
    #pragma omp barrier
}

int GetThreadCount() {
    cpu_set_t cs;
    CPU_ZERO(&cs);
    sched_getaffinity(0, sizeof(cs), &cs);

    int count = 0;
    for (int i = 0; i < CPU_SETSIZE; ++i)
        if (CPU_ISSET(i, &cs))
            ++count;

    return count;
}

double spectral_game(int N) {
    __attribute__((aligned(16))) double u[N];
    __attribute__((aligned(16))) double v[N], tmp[N];

    double vBv = 0.0;
    double vv = 0.0;

    #pragma omp parallel default(shared) num_threads(GetThreadCount())
    {
        int threadid = omp_get_thread_num();
        int threadcount = omp_get_num_threads();
        int chunk = N / threadcount;

        int begin = threadid * chunk;
        int end = (threadid < (threadcount - 1)) ? (begin + chunk) : N;

        for (int i = begin; i < end; i++)
            u[i] = 1.0;
        #pragma omp barrier

        for (int ite = 0; ite < 10; ++ite) {
            EvalAtATimesU(u, v, tmp, begin, end, N);
            EvalAtATimesU(v, u, tmp, begin, end, N);
        }

        double sumvb = 0.0, sumvv = 0.0;
        for (int i = begin; i < end; i++) {
            sumvv += v[i] * v[i];
            sumvb += u[i] * v[i];
        }

        #pragma omp critical
        {
            vBv += sumvb;
            vv += sumvv;
        }
    }

    return sqrt(vBv / vv);
}

int main(int argc, char *argv[]) {
    int N = ((argc >= 2) ? atoi(argv[1]) : 2000);
    printf("%.9f\n", spectral_game(N));
    return 0;
}