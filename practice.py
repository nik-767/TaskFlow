#Problem: nums = [0, 1, 0, 3, 12]. Aapko is array ke saare zeros (0) ko aakhri mein push karna hai, lekin bina koi naya list ([]) banaye! Jo bhi shift karna hai, isi nums ke andar element ko swap (Pattern 10) karke karo.(Hint: Ek pointer slow rakho jo zero ki position trace karega, aur ek fast jo numbers dhoondega).

nums = [0,1,0,3,12]
left = 0
right = 0

for i in range(len(nums)):
    if nums[i] != 0:
        nums[left] , nums[i] = nums[i] , nums[left]
        left += 1

print(nums)

#INDEX RETURM OF TWO POINTER
#Problem: Two Sum (Sorted Array)Aapko ek Sorted Array (ascending order mein) diya hai aur ek target sum diya hai. Aapko un do numbers ke indices (1-based index) return karne hain jinka sum target ke barabar ho.Rules:Aap koi extra space/dictionary use nahi kar sakte (Space Complexity must be O(1)).Ek pointer left = 0 par rakho aur dusra right = len(nums) - 1 par

nums = [2, 7, 11, 15]
target = 9
first = 0
last = len(nums) -1
while first < last:
    new = nums[first] + nums[last]
    if new == target:
        print(first + 1 , last + 1)
        break
    elif new < target:
        first += 1
    
    else:
        last -= 1