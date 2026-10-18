import java.util.Scanner;
public class J20 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int total = sc.nextInt();
        int count = sc.nextInt();
        int average = count == 0 ? 0 : total / count;
        if (count == 0) {
            System.out.println("undefined");
        } else {
            System.out.println(average);
        }
    }
}
