package main

import (
	"fmt"
	"math/rand"
	"time"
)

// isPrime проверяет, является ли число простым
func isPrime(n int) bool {
	if n <= 1 {
		return false
	}
	for i := 2; i*i <= n; i++ {
		if n%i == 0 {
			return false
		}
	}
	return true
}

// generatePrime генерирует простое число заданной длины в битах
func generatePrime(bits int) int {
	rand.Seed(time.Now().UnixNano())
	for {
		// Генерация случайного числа в пределах (2^(bits-1), 2^bits)
		primeCandidate := rand.Intn(1<<(bits)-1) + (1 << (bits - 1))
		if isPrime(primeCandidate) {
			return primeCandidate
		}
	}
}

// gcd возвращает наибольший общий делитель
func gcd(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

// modInverse находит модульный обратный элемент
func modInverse(a, p int) int {
	m0, x0, x1 := p, 0, 1
	if p == 1 {
		return 0
	}
	// Применяем расширенный алгоритм Евклида
	for a > 1 {
		// q — количество целых в делении
		q := a / p
		p, a = a%p, p
		x0, x1 = x1-q*x0, x0
	}
	if x1 < 0 {
		x1 += m0
	}
	return x1
}

// generateKeys генерирует публичный и закрытый ключи
func generateKeys(bits int) (publicKey, privateKey [3]int) {
	p := generatePrime(bits)
	g := rand.Intn(p-1) + 1 // Генератор g
	x := rand.Intn(p-2) + 1 // Закрытый ключ
	y := pow(g, x, p)       // Публичный ключ

	publicKey = [3]int{p, g, y}
	privateKey = [3]int{p, g, x}
	return
}

// pow возвращает (base^exp) % mod
func pow(base, exp, mod int) int {
	result := 1
	base = base % mod
	for exp > 0 {
		if exp%2 == 1 {
			result = (result * base) % mod
		}
		exp = exp >> 1
		base = (base * base) % mod
	}
	return result
}

// encrypt шифрует сообщение
func encrypt(publicKey [3]int, plaintext int) (int, int) {
	p, g, y := publicKey[0], publicKey[1], publicKey[2]
	k := rand.Intn(p-2) + 1
	for gcd(k, p-1) != 1 {
		k = rand.Intn(p-2) + 1
	}

	a := pow(g, k, p)                   // a = g^k % p
	b := (pow(y, k, p) * plaintext) % p // b = y^k * plaintext % p
	return a, b                         // Возвращаем (a, b)
}

// decrypt дешифрует сообщение
func decrypt(privateKey [3]int, ciphertext [2]int) int {
	p, _, x := privateKey[0], privateKey[1], privateKey[2]
	a, b := ciphertext[0], ciphertext[1]
	s := pow(a, x, p)               // s = a^x % p
	sInverse := modInverse(s, p)    // Находим обратное s
	plaintext := (b * sInverse) % p // plaintext = b * s^(-1) % p
	return plaintext
}

func main() {
	bits := 16 // Длина простого числа в битах
	publicKey, privateKey := generateKeys(bits)

	fmt.Println("Публичный ключ (p, g, y):", publicKey)
	fmt.Println("Закрытый ключ (p, g, x):", privateKey)

	// Шифрование
	message := 42 // Сообщение для шифрования
	a, b := encrypt(publicKey, message)
	fmt.Println("Зашифрованное сообщение (a, b):", a, b)

	// Дешифрование
	decryptedMessage := decrypt(privateKey, [2]int{a, b})
	fmt.Println("Расшифрованное сообщение:", decryptedMessage)
}
